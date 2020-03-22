from common.utils import PipelineUtils
PipelineUtils.getSpark()
from delta.tables import * # ignore pylint error 

class DeltaUtils:
    @staticmethod
    def getDeltaTable(table):
        deltaConfig = PipelineUtils.getConfig()['delta']
        path=deltaConfig['tables'][table]["path"]
        spark = PipelineUtils.getSpark()
        return DeltaTable.forPath(spark, path)

    # static method for merging incremental updates  into Delta tables
    @staticmethod
    def upsertMicroBatchToDelta(tableName,microBatchOutputDF, whereClause="table.id = updates.id"):
        deltaTable = DeltaUtils.getDeltaTable(tableName)
        return deltaTable.alias("table").merge(microBatchOutputDF.alias("updates"), whereClause)\
                .whenMatchedUpdateAll()\
                .whenNotMatchedInsertAll()\
                .execute()