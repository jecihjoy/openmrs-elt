import json
from pathlib import Path
import os
from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from kazoo.client import KazooClient
import time
from datetime import datetime


class PipelineUtils:

    @staticmethod
    def getConfig(dir=None):
        if (dir is None):
            dir = str(Path(str(Path.cwd()))) + '/config'
        with open(dir + '/config.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def getSparkConf():
        config = PipelineUtils.getConfig()['spark']
        packages = '--packages ' + ','.join(config['packages'])
        os.environ['PYSPARK_SUBMIT_ARGS'] = (packages + ' pyspark-shell')

        spark_conf = SparkConf().setAppName(config['appName']).setMaster(config['master'])
        if(config['conf']):
            for key in config['conf']:
                spark_conf.setIfMissing(key, config['conf'][key])
        return spark_conf

    @staticmethod
    def getSpark():
        if("spark" not in globals()):
            spark = SparkSession \
                .builder \
                .config(conf=PipelineUtils.getSparkConf()) \
                .getOrCreate()
            spark.sparkContext.setLogLevel("INFO") 
            globals()["spark"] = spark
        return globals()["spark"]
    
    @staticmethod
    def getStreamingContext():
        if("sparkSC" not in globals()):
            ssc_config = PipelineUtils.getConfig()['spark']['streaming']
            sc = PipelineUtils.getSpark().sparkContext
            ssc = StreamingContext(sc, ssc_config['batchDuration'])
            #ssc.checkpoint(ssc_config['checkpointDir'])
            globals()["sparkSC"] = ssc
        return globals()["sparkSC"]

    @staticmethod
    def getStreamingCheckpointPath():
        if("StreamingCheckpointPath" not in globals()):
            ssc_config = PipelineUtils.getConfig()['spark']['streaming']
            globals()["StreamingCheckpointPath"] = ssc_config['checkpointDir']
        return globals()["StreamingCheckpointPath"]

    @staticmethod
    def getMysqlOptions():
        spark = PipelineUtils.getSpark()
        mysql_config = PipelineUtils.getConfig()['mysql']
        url = 'jdbc:mysql://{}/{}?zeroDateTimeBehavior=convertToNull'.format(mysql_config['host'],
                                                                             mysql_config['openmrsDB'])
        return spark.read.format("jdbc"). \
            option("url", url). \
            option("useUnicode", "true"). \
            option("continueBatchOnError", "true"). \
            option("useSSL", "false"). \
            option("user", mysql_config['username']). \
            option("password", mysql_config['password']). \
            option("driver", "com.mysql.cj.jdbc.Driver")

    def getDataFromMySQL(self, tableName, config):
        if config:
            return  PipelineUtils.getMysqlOptions(). \
                option("dbtable", tableName). \
                option("partitionColumn", config['partitionColumn']). \
                option("fetchSize", config['fetchsize']). \
                option("lowerBound", config['lowerBound']). \
                option("upperBound", config['upperBound']). \
                option("numPartitions", config['numPartitions']). \
                load()
        else:
             return  PipelineUtils.getMysqlOptions(). \
                option("dbtable", tableName). \
                load()
    @staticmethod
    def getZookeeperInstance():
        if 'KazooSingletonInstance' not in globals():
            zkConfig = PipelineUtils.getConfig()['zookeeper']
            globals()['KazooSingletonInstance'] = KazooClient(zkConfig['servers'])
            globals()['KazooSingletonInstance'].start()
        return globals()['KazooSingletonInstance']
