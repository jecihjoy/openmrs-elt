import os
import sys
from pyspark import SparkContext, SparkConf
from batch.encounter_job import EncounterJob


def main():
    print(SparkConf().getAll())  # check if all packages are loaded
    job = EncounterJob()
    job.run()
    input("Press enter to exit ;)")


if __name__ == "__main__":
    main()
