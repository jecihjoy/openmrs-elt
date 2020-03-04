from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
import json
from pathlib import Path
import os


class BatchJob:

    @staticmethod
    def getConfig(dir=None):
        if (dir is None):
            dir = str(Path(str(Path.cwd()))) + '/config'
        with open(dir + '/config.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def getSpark():
        spark_config = BatchJob.getConfig()['spark']
        packages = '--packages ' + ','.join(spark_config['packages'])
        os.environ['PYSPARK_SUBMIT_ARGS'] = (packages + ' pyspark-shell')
        spark = SparkSession \
            .builder \
            .master(spark_config['master']) \
            .appName(spark_config['appName']) \
            .config("spark.executor.memory", '5g') \
            .config("spark.driver.memory", '20g') \
            .config('spark.sql.repl.eagerEval.enabled', True) \
            .config("jsonstore.rdd.partitions", 15000) \
            .config('spark.driver.maxResultSize', "20g") \
            .config("spark.cores.max", 32) \
            .config("spark.executor.cores", 8) \
            .config("spark.executor.heartbeatInterval", "10000000") \
            .config("spark.network.timeout", "10000000") \
            .config('spark.sql.crossJoin.enabled', True) \
            .config('spark.sql.autoBroadcastJoinThreshold', 0) \
            .config("spark.sql.shuffle.partitions", 1000) \
            .getOrCreate()
        spark.sparkContext.setLogLevel("INFO")
        return spark

    def getDataFromMySQL(self, tableName, config):
        spark = BatchJob.getSpark()
        mysql_config = self.getConfig()['mysql']
        url = 'jdbc:mysql://{}/{}?zeroDateTimeBehavior=convertToNull'.format(mysql_config['host'],
                                                                             mysql_config['openmrsDB'])
        return spark.read.format("jdbc"). \
            option("url", url). \
            option("useUnicode", "true"). \
            option("continueBatchOnError", "true"). \
            option("useSSL", "false"). \
            option("user", mysql_config['username']). \
            option("password", mysql_config['password']). \
            option("driver", "com.mysql.cj.jdbc.Driver"). \
            option("dbtable", tableName). \
            option("partitionColumn", config['partitionColumn']). \
            option("fetchSize", config['fetchsize']). \
            option("lowerBound", config['lowerBound']). \
            option("upperBound", config['upperBound']). \
            option("numPartitions", config['numPartitions']). \
            load()
