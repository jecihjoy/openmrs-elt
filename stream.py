import os
import sys
from pyspark import SparkContext, SparkConf
from streaming.encounter_job import EncounterJob


def main():
    print(SparkConf().getAll())  # check if all packages are loaded
    job = EncounterJob()
    job.run()

if __name__ == "__main__":
    main()
