# coding: utf-8

import time
from datetime import datetime
from pyspark.sql import SparkSession, Row, SQLContext, Window
from pyspark.sql.types import StructType, StringType, StructField, BooleanType, IntegerType, ArrayType, TimestampType, \
    DoubleType
from pyspark import SparkContext
import pyspark.sql.functions as f
from batch.job import BatchJob


class EncounterJob(BatchJob):

    # responsible for ingesting obs with non-null encounters
    def ingest_obs_with_encounter(self):
        obs = super().getDataFromMySQL('obs_with_encounter', {
            'partitionColumn': 'encounter_id',
            'fetchsize': 100000,
            'lowerBound': 1,
            'upperBound': 8000000,
            'numPartitions': 5000})
        return self.sanitize_obs(obs)

    # responsible for ingesting obs with null encounters
    def ingest_obs_without_encounter(self):
        obs = super().getDataFromMySQL('obs_with_null_encounter', {
            'partitionColumn': 'obs_id',
            'fetchsize': 65907,
            'lowerBound': 1,
            'upperBound': 270678501,
            'numPartitions': 5000}) \
            .withColumn('encounter_id', f.col('obs_id') + 100000000) \
            .withColumn('order_id', f.lit('null')) \
            .withColumn('order_concept_id', f.lit('null'))
        return self.sanitize_obs(obs)

    # responsible for ingesting orders
    def ingest_orders(self):
        orders = super().getDataFromMySQL('encounter_orders', {
            'partitionColumn': 'order_id',
            'fetchsize': 5083,
            'lowerBound': 1,
            'upperBound': 124000,
            'numPartitions': 24})
        return self.sanitize_orders(orders)

    # TODO Remove all static methods into helper class | code could be reused in streaming-pipeline
    # static method for restructuring  obs into expected format
    @staticmethod
    def sanitize_obs(obs):
        return obs \
            .withColumn('value',
                        f.when(f.col('value_numeric').isNotNull(), f.col('value_numeric').cast('string')) \
                        .when(f.col('value_text').isNotNull(), f.col('value_text')) \
                        .when(f.col('value_drug').isNotNull(), f.col('value_drug')) \
                        .when(f.col('value_datetime').isNotNull(), f.col('value_datetime').cast('string')) \
                        .when(f.col('value_coded').isNotNull(), f.col('value_coded').cast('string'))
                        ) \
            .withColumn('value_type',
                        f.when(f.col('value_numeric').isNotNull(), f.lit('numeric')) \
                        .when(f.col('value_text').isNotNull(), f.lit('text')) \
                        .when(f.col('value_drug').isNotNull(), f.lit('drug')) \
                        .when(f.col('value_datetime').isNotNull(), f.lit('datetime')) \
                        .when(f.col('value_coded').isNotNull(), f.lit('coded'))) \
            .orderBy('encounter_datetime').groupBy('encounter_id') \
            .agg(
                f.first('patient_id').alias('patient_id'),
                f.first('location_id').alias('location_id'),
                f.first('visit_id').alias('visit_id'),
                f.first('encounter_datetime').alias('encounter_datetime'),
                f.first('encounter_type').alias('encounter_type'),
                f.first('gender').alias('gender'),
                f.first('dead').alias('dead'),
                f.first('death_date').alias('death_date'),
                f.first('uuid').alias('patient_uuid'),
                f.first('visit_type_id').alias('visit_type_id'),
                f.first('birthdate').alias('birthdate'),
                f.to_json(f.collect_list(f.struct(
                    f.col('obs_id').alias('obs_id'),
                    f.col('voided').alias('voided'),
                    f.col('concept_id').alias('concept_id'),
                    f.col('obs_datetime').alias('obs_datetime'),
                    f.col('value').alias('value'),
                    f.col('value_type').alias('value_type'),
                    f.col('obs_group_id').alias('obs_group_id'),
                    f.col('parent_concept_id').alias('parent_concept_id'),
                ))).alias('obs'))

    # static method for restructuring  obs into expected format
    @staticmethod
    def sanitize_orders(orders):
        return orders \
            .withColumnRenamed('concept_id', 'order_concept_id') \
            .orderBy('encounter_datetime').groupBy('encounter_id') \
            .agg(
                f.col('encounter_id'),
                f.first('patient_id').alias('patient_id'),
                f.first('location_id').alias('location_id'),
                f.first('visit_id').alias('visit_id'),
                f.first('encounter_datetime').alias('encounter_datetime'),
                f.first('encounter_type').alias('encounter_type'),
                f.first('gender').alias('gender'),
                f.first('dead').alias('dead'),
                f.first('death_date').alias('death_date'),
                f.first('uuid').alias('patient_uuid'),
                f.first('visit_type_id').alias('visit_type_id'),
                f.first('birthdate').alias('birthdate'),
                f.to_json(f.collect_list(f.struct(
                    f.col('order_id').alias('order_id'),
                    f.col('order_concept_id').alias('order_concept_id'),
                    f.col('date_activated').alias('date_activated'),
                    f.col('voided').alias('voided'),
                ))).alias('orders'))

    # start spark job
    def run(self):

        print("Encounter Batch Started at =", datetime.now().time())

        # ingest all components
        orders = self.ingest_orders()
        obs_without_encounter = self.ingest_obs_without_encounter()
        obs_with_encounter = self.ingest_obs_with_encounter()

        # union obs and join
        all_obs = obs_with_encounter.union(obs_without_encounter)
        obs_orders = all_obs\
            .join(orders, on=['encounter_id'], how='outer') \
            .select(
                    f.col('encounter_id'),
                    f.coalesce(all_obs.patient_id, orders.patient_id).alias('patient_id'),
                    f.coalesce(all_obs.location_id, orders.location_id).alias('location_id'),
                    f.coalesce(all_obs.visit_id, orders.visit_id).alias('visit_id'),
                    f.coalesce(all_obs.encounter_datetime, orders.encounter_datetime).alias('encounter_datetime'),
                    f.coalesce(all_obs.encounter_type, orders.encounter_type).alias('encounter_type'),
                    f.coalesce(all_obs.dead, orders.dead).alias('dead'),
                    f.coalesce(all_obs.gender, orders.gender).alias('gender'),
                    f.coalesce(all_obs.death_date, orders.death_date).alias('death_date'),
                    f.coalesce(all_obs.patient_uuid, orders.patient_uuid).alias('patient_uuid'),
                    f.coalesce(all_obs.visit_type_id, orders.visit_type_id).alias('visit_type_id'),
                    f.coalesce(all_obs.birthdate, orders.birthdate).alias('birthdate'),
                    all_obs.obs,
                    orders.orders
                    )

        return obs_orders