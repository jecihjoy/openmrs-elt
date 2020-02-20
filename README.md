# Openmrs ELT Pipeline

This projet demonstrates how to perform batch process for generating flat_obs i.e Extract part ofr ELT. Data is extracted from openmrs and storerd in delta lake i.e flat_obs

## Getting started

### 1. Install Pyspark
```
conda install pyspark

```

### 2. Configure your Mysql setting in config/config.json
```
"mysql": {
    "host": "127.0.0.1",
    "port": "3306",
    "username": "root",
    "password": "debezium",
    "openmrsDB": "openmrs"
  }

```

### 3. Create all mysql views by executing mysql scripts in /views folder. for this demo just execute obs_view.sql

```
mysql db_name < obs_view.sql
```

### 4. Execute the batch job as demonstrated in [Jupyter notebook](example.ipynb)

```
jupyter notebook example.ipynb
```

