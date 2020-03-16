import os
import sys
from pyspark import SparkContext, SparkConf
from batch.encounter_job import EncounterJob


def main():
    print(SparkConf().getAll())  # check if all packages are loaded
    job = EncounterJob()
    flat_obs = job.run()
    flat_obs.coalesce(24).write.format("delta").mode("overwrite").save("flat_obs_orders.delta")
    input("Press enter to exit ;)")


if __name__ == "__main__":
    main()
