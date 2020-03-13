# coding: utf-8

import time
from datetime import datetime
from pyspark.sql import SparkSession, Row, SQLContext, Window
from pyspark.sql.types import StructType, StringType, StructField, BooleanType, IntegerType, ArrayType, TimestampType, \
    DoubleType
from pyspark import SparkContext
import pyspark.sql.functions as f
from common.job import Job
from common.encounter_helper import EncounterHelper


class EncounterJob(Job):

    # responsible for ingesting obs with non-null encounters
    def ingest_obs_with_encounter(self):
        obs = super().getDataFromMySQL('obs_with_encounter', {
            'partitionColumn': 'encounter_id',
            'fetchsize': 100000,
            'lowerBound': 1,
            'upperBound': 8000000,
            'numPartitions': 5000})
        return EncounterHelper.sanitize_obs(obs)

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
        return EncounterHelper.sanitize_obs(obs)

    # responsible for ingesting orders
    def ingest_orders(self):
        orders = super().getDataFromMySQL('encounter_orders', {
            'partitionColumn': 'order_id',
            'fetchsize': 5083,
            'lowerBound': 1,
            'upperBound': 124000,
            'numPartitions': 24})
        return EncounterHelper.sanitize_orders(orders)

    # start spark job
    def run(self):

        print("Encounter Batch Started at =", datetime.now().time())

        # ingest all components
        orders = self.ingest_orders()
        obs_without_encounter = self.ingest_obs_without_encounter()
        obs_with_encounter = self.ingest_obs_with_encounter()

        # union obs and join
        all_obs = obs_with_encounter.union(obs_without_encounter)
        obs_orders = EncounterHelper.join_obs_orders(all_obs,orders)

        return obs_orders