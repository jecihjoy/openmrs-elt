
import os
import sys
from pyspark import SparkContext, SparkConf
from batch.encounter_job import EncounterJob



def main():
  print(SparkConf().getAll()) # check of all packages are loaded
  job = EncounterJob()
  flat_obs = job.run()
  print(flat_obs.head())
  flat_obs.write.format("delta").save("flat_obs")
  
if __name__== "__main__":
  main()



