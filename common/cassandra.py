import time
import os
from datetime import datetime
from common.utils import PipelineUtils
PipelineUtils.getSpark()

class CassandraUtils:

    @staticmethod
    def sourceFromCassandra(table):
        return PipelineUtils.getSpark().read\
            .format("org.apache.spark.sql.cassandra")\
            .options(table=table, keyspace="elt")\
            .load()

    @staticmethod
    def deleteFromCassandra(table,encounter_ids):
        print("TODO: Implement Del", encounter_ids)

    @staticmethod
    def sinkToCassandra(df, table, mode="append"):
        start_time = datetime.utcnow()
        if mode=="append":
            df.write.format("org.apache.spark.sql.cassandra")\
                        .options(table=table, keyspace="elt")\
                        .mode("append")\
                        .save()
        else:
            df.write.format("org.apache.spark.sql.cassandra")\
                        .options(table=table, keyspace="elt")\
                        .option("confirm.truncate", "true")\
                        .mode("overwrite")\
                        .save()
        end_time = datetime.utcnow()
        print("Took {0} minutes to sink to cassandra".format((end_time - start_time).total_seconds()/60))