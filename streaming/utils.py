from common.utils import PipelineUtils
from kazoo.client import KazooClient
from pyspark.streaming.kafka import TopicAndPartition


class StreamingUtils:

    @staticmethod
    def read_offsets(topics):
        try:
            zk = PipelineUtils.getZookeeperInstance()
            from_offsets = {}
            for topic in topics:
                for partition in zk.get_children(f'/consumers/{topic}'):
                    topic_partion = TopicAndPartition(topic, int(partition))
                    offset = int(zk.get(f'/consumers/{topic}/{partition}')[0])
                    from_offsets[topic_partion] = offset
            print("Previous offset -->", from_offsets)
            return from_offsets
        except:
            print("An unexpected error occurred while reading offset")
            pass

    @staticmethod
    def save_offsets(rdd):
        print("Saving offset | Exactly Once Semantics")
        zk = PipelineUtils.getZookeeperInstance()
        for offset in rdd.offsetRanges():
            path = f"/consumers/{offset.topic}/{offset.partition}"
            zk.ensure_path(path)
            zk.set(path, str(offset.untilOffset).encode())
    