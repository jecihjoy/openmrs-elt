# Simulations

Streaming 100 records every 20 seconds | 100 million synthetic observations(1 million encounters).


## Results
| Resources                 | Containers                                       | Simulation                            | Batch          | Streaming              | Streaming Latency |
|---------------------------|--------------------------------------------------|---------------------------------------|----------------|------------------------|-------------------|
| "4 cores, 4GB RAM, SSD"   | "6: OpenMRS, MySQL,Debezium \(zk,kf,cn\), Spark" | "100 rec per 20 sec, 100 million obs" | 2 hour 52 mins | 33 secs per microbatch | AVG 1 minutes     |
| "8 cores, 8GB RAM, SSD"   | "6: OpenMRS, MySQL,Debezium \(zk,kf,cn\), Spark" | "100 rec per 20 sec, 100 million obs" | 1 hour 20 mins | 11 secs per microbatch | < 17 secs         |
| "8 cores, 16GB RAM, SSD"  | "6: OpenMRS, MySQL,Debezium \(zk,kf,cn\), Spark" | "100 rec per 20 sec, 100 million obs" | 42 mins        | 9 secs per microbatch  | < 17 secs         |
| "16 cores, 16GB RAM, SSD" | "6: OpenMRS, MySQL,Debezium \(zk,kf,cn\), Spark" | "100 rec per 20 sec, 100 million obs" | 16 mins        | 5 secs per microbatch  | < 8 secs          |

