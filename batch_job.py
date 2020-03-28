import os
import sys
from pyspark import SparkContext, SparkConf
from batch.encounter_job import EncounterJob


def main():
    log_file = open("batch.log","w")
    sys.stdout = log_file
    
    print(SparkConf().getAll())  # check if all packages are loaded
    job = EncounterJob()
    job.run()

    old_stdout = sys.stdout
    sys.stdout = old_stdout
    log_file.close()
    input("Press enter to exit ;)")


if __name__ == "__main__":
    main()
