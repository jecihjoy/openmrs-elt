# OpenMRS CDC

The goal of this tool is to provide realtime downstream consumption of consumption of openmrs incremental updates for  analytics or data science workflows.

- Reads change events from the openmrs database log.
- Streams them to kafka.
- Consume using Kafka

## Requirements
Make sure you have the latest docker and docker compose
1. Install [Docker](http://docker.io).
2. Install [Docker-compose](http://docs.docker.com/compose/install/).
3. Configure /cdc/docker-compose.yaml (ensure that you set the host IPs appropriately)

# Dev Deployment
You will only have to run only 3 commands to get the entire cluster running. 

- This will install  5 containers with openmrs ref-app (mysql, kafka, connect (dbz), openmrs, zookeeper, kafdrop)
- For deployment on existing instances of openmrs, please see instructions on Production Deployment section


## Getting started 

Open up your terminal and run these commands:


 1. Set debezium version environment variable: .8, .9, or 1.0

    ```shell
    export DEBEZIUM_VERSION=0.9
    ```
 2. Configure kafka ADVERTISED_HOST_NAME in docker-compose.yaml before bring up the  container - this important for consumption outside the the docker network.

 3. Bring up the cluster by running

    ```shell
    docker-compose -f docker-compose.yaml up
    ```
 4. After waiting for 2 to 3 minutes for the cluster to install,  start the MySQL-debezium connector (VERY IMPORTANT)

    ```shell
    curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-mysql.json


    ```

 ## Consuming messages from a Kafka topic [obs,encounter,person, e.t.c]

 All you have to do is change the topic to  --topic dbserver1.openmrs.<tableName> and run this command
 
 ```shell
docker-compose -f docker-compose.yaml exec kafka /kafka/bin/kafka-console-consumer.sh \
     --bootstrap-server kafka:9092 \
     --from-beginning \
     --property print.key=true \
     --topic dbserver1.openmrs.obs
 ```

 - The same can be accomplished using python, scala, and java, please visit https://spark.apache.org/docs/latest/streaming-kafka-integration.html
 - Additionally, you will also need to configure kafka ADVERTISED_HOST_NAME (in the docker compose) for you to consume messages outside docker network


## Monitoring Kafka and Zookeeper
To monitor topic ingress/egress and other important metrics:

   - KafkaHQ: http://localhost:7777/
   - Kafdrop: http://localhost:9191/
   - ZK: http://localhost:5555/

This can be substituted by better monitoring tools like lenses

## Openmrs App
Openmrs Application will be eventually accessible on http://localhost:8080/openmrs.
Credentials on shipped demo data:
  - Username: admin
  - Password: Admin123
  
## MySQL client
```
docker-compose -f docker-compose.yaml exec mysql bash -c 'mysql -u $MYSQL_USER -p$MYSQL_PASSWORD openmrs'
```    

## Schema Changes Topic
```
docker-compose -f docker-compose.yaml exec kafka /kafka/bin/kafka-console-consumer.sh     --bootstrap-server kafka:9092     --from-beginning     --property print.key=true     --topic schema-changes.openmrs
```

## How to Verify MySQL connector (Debezium)
``` 
curl -H "Accept:application/json" localhost:8083/connectors/
```

## Shut down the cluster
```  
docker-compose -f docker-compose.yaml down
```


# Production Deployment

In most instances, openmrs and production database are pre-deployed. As such you only need to configure your DB to support row-based replication and remove unnecessary containers e.g mysql and openmrs from the docker-compose file. You are advised to do deploy this workflow at the slave database in order to minimize analytics interference with prod

There are a few configuration options required to ensure your database can participate in replication. 

- The db user responsible for replication within MySQL  must exist and have at least the following permissions on the source database:
    - SELECT
    - RELOAD
    - SHOW DATABASES
    - REPLICATION SLAVE
    - REPLICATION CLIENT

- The source MySQL instance must have the following server configs set to generate binary logs in a format Spark can consume:
    - server_id = <value>
    - log_bin = <value>
    - binlog_format = row
    - binlog_row_image = full
- Depending on server defaults and table size, it may also be necessary to increase the binlog retention period.

An example of mysql.conf has bee provided with the above configurations

```
# ----------------------------------------------
# Enable the binlog for replication & CDC
# ----------------------------------------------

# Enable binary replication log and set the prefix, expiration, and log format.
# The prefix is arbitrary, expiration can be short for integration tests but would
# be longer on a production system. Row-level info is required for ingest to work.
# Server ID is required, but this will vary on production systems
server-id         = 223344
log_bin           = mysql-bin
expire_logs_days  = 1
binlog_format     = row

```

For more information on how to deploy using different DB, other than mysql, please visit
https://debezium.io


# Troubleshooting

- **code 137:** In order to avoid crashing of containers i.e code 137, please increase memory size and cpu of your docker VM to >= 8gb and >=4 cores as shown in the figure below
- **error: org.apache.spark.SparkException: Couldn't find leader offsets for Set** : This error throws when ADVERTISED_HOST_NAME or KAFKA_ADVERTISED_HOST_NAME is not accessible outside the docker network- please configure it to your LAN IP : https://stackoverflow.com/questions/39273878/spark-streaming-kafka-couldnt-find-leader-offsets-for-set

# TODO
* Automate this deployment
* Make it configurable
* Make it support different DBS
* Provide examples for scala and java
* Consider K8s deployments
* A python/spark package would be nice
* Add ability to scale kafka brokers

