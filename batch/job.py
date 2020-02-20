from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
import json
from pathlib import Path
import os

class Job: 

    @staticmethod
    def getConfig(dir=None):
        if(dir is None):
                dir = str(Path(str(Path.cwd()))) + '/config'
        with open(dir + '/config.json', 'r') as f:
            return json.load(f)
    
    @staticmethod
    def getSpark():
        spark_config = Job.getConfig()['spark']
        packages = '--packages '+','.join(spark_config['packages'])
        os.environ['PYSPARK_SUBMIT_ARGS'] =  (packages+' pyspark-shell')
        spark = SparkSession\
        .builder\
        .config("spark.executor.memory", '10g') \
        .config("spark.driver.memory",'40g') \
        .config('spark.sql.repl.eagerEval.enabled', True)\
        .config("jsonstore.rdd.partitions", 15000)\
        .config('spark.driver.maxResultSize', "15000M")\
        .config('spark.sql.crossJoin.enabled', True)\
        .config('spark.sql.autoBroadcastJoinThreshold', 0)\
        .config("spark.sql.shuffle.partitions", 1000)\
        .getOrCreate()
        spark.sparkContext.setLogLevel("INFO") 
        return spark

    def getDataFromMySQL(self, tableName, config):  
       
        spark = Job.getSpark()
        mysql_config = self.getConfig()['mysql']
        url='jdbc:mysql://{}/{}?zeroDateTimeBehavior=convertToNull'.format(mysql_config['host'], mysql_config['openmrsDB'])
        return spark.read.format("jdbc").\
          option("url", url).\
          option("useUnicode", "true").\
          option("continueBatchOnError","true").\
          option("useSSL", "false").\
          option("user", mysql_config['username']).\
          option("password", mysql_config['password']).\
          option("driver","com.mysql.jdbc.Driver").\
          option("dbtable",tableName).\
          option("partitionColumn", config['partitionColumn']).\
          option("fetchSize", config['fetchsize']).\
          option("lowerBound", config['lowerBound']).\
          option("upperBound", config['upperBound']).\
          option("numPartitions", config['numPartitions']).\
          load()
    
 