from pyspark.sql import SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
import json
from pathlib import Path
import os


class Job:

    @staticmethod
    def getConfig(dir=None):
        if (dir is None):
            dir = str(Path(str(Path.cwd()))) + '/config'
        with open(dir + '/config.json', 'r') as f:
            return json.load(f)

    @staticmethod
    def getSparkConf():
        config = Job.getConfig()['spark']
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
                .config(conf=Job.getSparkConf()) \
                .getOrCreate()
            spark.sparkContext.setLogLevel("INFO") 
            globals()["spark"] = spark
        return globals()["spark"]
    
    @staticmethod
    def getStreamingContext():
        if("sparkSC" not in globals()):
            ssc_config = Job.getConfig()['spark']['streaming']
            sc = Job.getSpark().sparkContext
            ssc = StreamingContext(sc, ssc_config['batchDuration'])
            ssc.checkpoint(ssc_config['checkpointDir'])
            globals()["sparkSC"] = ssc
        return globals()["sparkSC"]

    @staticmethod
    def getMysqlOptions():
        spark = Job.getSpark()
        mysql_config = Job.getConfig()['mysql']
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
            return  Job.getMysqlOptions(). \
                option("dbtable", tableName). \
                option("partitionColumn", config['partitionColumn']). \
                option("fetchSize", config['fetchsize']). \
                option("lowerBound", config['lowerBound']). \
                option("upperBound", config['upperBound']). \
                option("numPartitions", config['numPartitions']). \
                load()
        else:
             return  Job.getMysqlOptions(). \
                option("dbtable", tableName). \
                load()


    