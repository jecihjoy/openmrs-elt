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

### 2. Configure your Mysql setting in config/config.json (**rename config.example.json to config.json**)
```
"mysql": {
    "host": "127.0.0.1",
    "port": "3306",
    "username": "root",
    "password": "debezium",
    "openmrsDB": "openmrs"
  }

```

### 3. Create all mysql views by executing mysql scripts in /views folder.

```
mysql db_name < views/*.sql
```

### 4. Execute the batch job as demonstrated below

```
python3 batch_job.py

```


### 5. Execute the streaming job - use Airflow to Schedule
Before executing this script, please ensure you deploy debezium/kafka cluster (OpenMRS CDC) demonstrated in [CDC](cdc/README) 

```
python3 streaming_job.py

```

Alternatively, you can checkout example of streaming job demonstrated in [Jupyter notebook](streaming-example.ipynb)