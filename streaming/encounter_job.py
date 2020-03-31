# coding: utf-8

import time
import json
import datetime
from pyspark.sql import SparkSession, Row, SQLContext, Window
from pyspark.sql.types import StructType, StringType, StructField, BooleanType, IntegerType, ArrayType, TimestampType, \
    DoubleType
from pyspark import SparkContext
import pyspark.sql.functions as f
from pyspark.streaming.kafka import KafkaUtils
from common.utils import PipelineUtils
from common.encounter_helper import EncounterHelper
from common.delta import DeltaUtils
from streaming.utils import StreamingUtils


class EncounterJob(PipelineUtils):
    
    offsetRanges = None

    # responsible for ingesting obs with non-null encounters
    def ingest_obs_with_encounter(self,ids, filterBy='encounter_id'):
        ids=','.join(map(str, ids))
        query = """(SELECT * FROM obs_with_encounter
               where {0} in ({1})) AS tmp
              """.format(filterBy,ids)
        obs = super().getDataFromMySQL(query,None)
        return EncounterHelper.sanitize_obs(obs)

    # responsible for ingesting obs with null encounters
    def ingest_obs_without_encounter(self,patient_ids):
        patient_ids=','.join(map(str, patient_ids))
        query ="""(SELECT * FROM obs_with_null_encounter 
                        where patient_id in ({0})) AS tmp
                        """.format(patient_ids)
        obs = super().getDataFromMySQL(query,None)\
            .withColumn('encounter_id', f.col('obs_id') + 10000000000) \
            .withColumn('order_id', f.lit('null')) \
            .withColumn('order_concept_id', f.lit('null'))
        return EncounterHelper.sanitize_obs(obs)

    # responsible for ingesting orders
    def ingest_orders(self,ids, filterBy='encounter_id'):
        ids=','.join(map(str, ids))
        query = """(SELECT * FROM encounter_orders
               where {0} in ({1})) AS tmp
              """.format(filterBy,ids)
        orders = super().getDataFromMySQL(query,None)             
        return EncounterHelper.sanitize_orders(orders)

    # Function to upsert flat_bs microBatchOutputDF into Delta Lake table using merge
    @staticmethod
    def sinkFlatObsToDelta(microbatch, batchId):
        DeltaUtils.upsertMicroBatchToDelta("flat_obs_orders", # delta tablename
                                          microbatch, # microbatch
                                          "table.encounter_id = updates.encounter_id" # where clause condition
                                          )
    @staticmethod
    def storeOffsetRanges(rdd):
        if not rdd.isEmpty():
            StreamingUtils.save_offsets(rdd)
        return rdd


    # responsible for rebuilding changed encounter data
    def upsert_encounter_microbatch(self, rdd):
        try:

            collected = rdd.collect()
            records = len(collected) 

            if records> 0:
                start_time = datetime.datetime.utcnow()
                encounter_ids = []
                person_ids = []
                
                print("---Upserting Encounter Micro-Batch--- ")
                print("Starting Time: " + time.ctime())
                for person in collected:
                    person_ids.append(person["person_id"])
                    for encounter in person["encounters"]:
                        encounter_ids.append(encounter)

                print("CDC: # Patient IDs in Microbatch --> ", len(person_ids))
                print("CDC: # Encounter IDs in Microbatch --> ", len(encounter_ids))

                # ingest all components
                all_obs = self.ingest_obs_with_encounter(encounter_ids, 'encounter_id')\
                    .union(self.ingest_obs_without_encounter(person_ids))
                orders = self.ingest_orders(encounter_ids, 'encounter_id')
                
                # upsert to delta lake
                self.sinkFlatObsToDelta(EncounterHelper.join_obs_orders(all_obs,orders),0)

                end_time = datetime.datetime.utcnow()
                print("Took {0} seconds".format((end_time - start_time).total_seconds()))


        except:
            print("An unexpected error occurred while upserting encounter microbatch")
            raise
    
    # responsible for rebuilding changed data for patient/s
    def upsert_patient_microbatch(self, rdd):
        try:

            collected = rdd.collect()
            records = len(collected) 
            if records> 0:
                start_time = datetime.datetime.utcnow()
                print("---Upserting Patient Micro-Batch--- ")
                print("Starting Time: " + time.ctime())
                patient_ids = []
                for row in collected:
                    patient_ids.append(row["person_id"])
                print("CDC: # Patient IDs in Microbatch --> ", len(patient_ids))

                # ingest all components
                all_obs = self.ingest_obs_with_encounter(patient_ids, 'patient_id') \
                    .union(self.ingest_obs_without_encounter(patient_ids))
                orders = self.ingest_orders(patient_ids, 'patient_id')

                # upsert to delta lake
                self.sinkFlatObsToDelta(EncounterHelper.join_obs_orders(all_obs,orders),0)

                end_time = datetime.datetime.utcnow()
                print("Took {0} seconds".format((end_time - start_time).total_seconds()))
                
        except:
            print("An unexpected error occurred while upserting patient microbatch")
            raise

    # responsible for deleting voided encounters
    def void_encounter_microbatch(self, rdd):
        try:

            collected = rdd.collect()
            records = len(collected) 
            if records> 0:
                start_time = datetime.datetime.utcnow()
                print("---Voiding Encounter Micro-Batch--- ")
                print("Starting Time: " + time.ctime())
                encounter_ids = []
                for row in collected:
                    encounter_ids.append(row["encounters"])
                print("CDC: # Encounter IDs in Microbatch --> ", records)
                encounter_ids=','.join(map(str, encounter_ids))
                deltaTable = DeltaUtils.getDeltaTable("flat_obs_orders")
                deltaTable.delete("encounter_id IN ({0})".format(encounter_ids))
                end_time = datetime.datetime.utcnow()
                print("Took {0} seconds".format((end_time - start_time).total_seconds()))

        except:
            print("An unexpected error occurred while voiding encounter microbatch")
            raise

    # start spark streaming job
    def run(self):

        print("Encounter Streaming Job Started at =", datetime.datetime.utcnow())
        kafka_config = super().getConfig()['kafka']['encounter-obs-orders']
        ssc= super().getStreamingContext()
        # get previous offset fromOffsets=from_offsets
        from_offsets=StreamingUtils.read_offsets(kafka_config['topics'])
        # create kafka DS
        kafka_stream = KafkaUtils\
              .createDirectStream(ssc,topics=kafka_config['topics'],
              kafkaParams=kafka_config['config'], fromOffsets=from_offsets)\
            .transform(self.storeOffsetRanges) # store offset 
              
        direct_stream = kafka_stream.map(lambda msg: json.loads(msg[1]))
        obs_stream = direct_stream \
                .filter(lambda msg: 'obs.Envelope' in msg['schema']['name']) \
                .map(lambda msg: msg['payload']['after']) \
                .map(lambda a: Row(**a))

        orders_stream = direct_stream \
                .filter(lambda msg: 'orders.Envelope' in msg['schema']['name']) \
                .map(lambda msg: msg['payload']['after'])\
                .map(lambda a: Row(**a))

        encounter_stream = direct_stream \
                .filter(lambda msg: 'encounter.Envelope' in msg['schema']['name']) \
                .map(lambda msg: msg['payload']['after'])\
                .map(lambda a: Row(**a))

        person_stream = direct_stream \
            .filter(lambda msg: 'person.Envelope' in msg['schema']['name']) \
            .map(lambda msg: msg['payload']['after'])\
            .map(lambda a: Row(**a))
        
        # extract obs with encounter IDs and convert into {encounter_id, person_id} tuple
        obs_with_enc_stream = obs_stream.filter(lambda a: a['encounter_id'] is not None)\
            .map(lambda row: (row['encounter_id'], row['person_id']))
        
        # extract obs with  null encounters and convert into {person_id, None} tuple
        obs_with_null_enc_stream  = obs_stream.filter(lambda a: a['encounter_id'] is None)\
            .map(lambda row: (row['person_id'], None))

        # convert orders and obs with encounters into a tuple of encouter_id and person_id then 
        # union the orders and obs stream then extract distinct encounter id then
        # convert into (person_id, encounter_id) tuple from (encounter_id, person_id) tuple
        # join obs without encounters with the enc_obs_orders for processing then
        # group by patient_id to get distinct patients
        enc_obs_orders = orders_stream.map(lambda row: (row['encounter_id'], row['patient_id']))\
            .union(obs_with_enc_stream)\
            .reduceByKey(lambda x, y: x)\
            .map(lambda tpl: (tpl[1], tpl[0]))\
            .union(obs_with_null_enc_stream)\
            .groupByKey()\
            .map(lambda x : Row(person_id=x[0], encounters=list(filter(None.__ne__, x[1]))))
        
        # perform incremental updates for encounter, obs, and orders and save to delta
        print('Event Enc Obs Orders: ', enc_obs_orders.pprint())
        enc_obs_orders.foreachRDD(lambda rdd: self.upsert_encounter_microbatch(rdd))

        # update patient details that have changed 
        person_stream=person_stream.map(lambda row: Row(person_id=row['person_id']))
        print('Event Person Enc: ', person_stream.pprint())
        person_stream.foreachRDD(lambda rdd: self.upsert_patient_microbatch(rdd))

        # Propagate deletion of voided encounters from delta lake
        voided_encounter_stream =encounter_stream.filter(lambda a: a['voided']==1)\
           .map(lambda row: Row( encounters=row['encounter_id']))
        print('Event Voided Enc: ', voided_encounter_stream.pprint())
        voided_encounter_stream.foreachRDD(lambda rdd: self.void_encounter_microbatch(rdd))

        ssc.checkpoint(super().getStreamingCheckpointPath())
        ssc.start()
        ssc.awaitTermination()