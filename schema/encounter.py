import json
import os
import time
from pyspark.sql.types import *
import pyspark.sql.functions as f
from pyspark.sql.functions import udf
from pyspark.sql.window import Window
from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext, SparkSession
import time
import datetime


class Model:

    @staticmethod
    def get_orders_schema():
        return ArrayType(
                StructType([
                    StructField('order_id',  LongType()   , True),
                    StructField('order_concept_id',  IntegerType()   , True),
                    StructField('date_activated',  TimestampType()   , True),
                    StructField('voided',  BooleanType()   , True)
                ]))



    @staticmethod
    def get_obs_schema():
        return ArrayType(StructType([
            StructField('obs_id', LongType(), True),
            StructField('voided', BooleanType(), True),
            StructField('concept_id', IntegerType(), True),
            StructField('obs_datetime', TimestampType(), True),
            StructField('value', StringType(), True),
            StructField('value_type', StringType(), True),
            StructField('obs_group_id', IntegerType(), True),
            StructField('parent_concept_id', IntegerType(), True)
        ]))
    