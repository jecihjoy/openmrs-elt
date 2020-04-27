# Openmrs ELT Pipeline

The goal of this tool is to provide batch abd near-realtime transformation of OpenMRS data for analytics or data science workflows. This project demonstrates how to perform batch and streaming process for generating flat_obs i.e Extract part of the ELT.  

* Batch - Data is extracted from OpenMRS and stored in delta lake (tables).
* Streaming - incremental updates are captured then streamed to the delta tables 

## Getting started

### 1. Install Requirements
```
pip install pyspark:2.5.4
pip install kazoo

```

### 2. Deploy the debezium/kafka cluster (OpenMRS CDC) demonstrated in [CDC](cdc/README.md) 

Use version .9 of debezium, version 1.0 doesn't support python API

### 3. Rename config/config.example.json to config/config.json

set parameters appropriately, should work using default settings

### 4. Check if all the MySQL views are created - if not create all mysql views by executing mysql scripts in /views folder.

```
mysql db_name < views/*.sql
```

### 5. Execute the batch job as demonstrated below

```
python3 batch_job.py

```


### 6. Execute the streaming job - use Airflow to Schedule
Before executing this script, please ensure you deploy debezium/kafka cluster (OpenMRS CDC) correctly demonstrated in [CDC](cdc/README) 

```
python3 streaming_job.py

```

Alternatively, you can checkout example of streaming job demonstrated in [Jupyter notebook](streaming-example.ipynb)
