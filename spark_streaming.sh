#!/bin/bash

# Start the Spark container if not already running
docker start spark || docker run -d --name spark bitnami/spark:latest

docker cp hadoop-namenode:/etc/hadoop/core-site.xml /tmp/core-site.xml
docker cp hadoop-namenode:/etc/hadoop/hdfs-site.xml /tmp/hdfs-site.xml
docker exec -it --user root spark /bin/bash -c "
  mkdir -p /opt/hadoop-2.7.7/etc/hadoop &&
  mv /tmp/core-site.xml /opt/hadoop-2.7.7/etc/hadoop/core-site.xml &&
  mv /tmp/hdfs-site.xml /opt/hadoop-2.7.7/etc/hadoop/hdfs-site.xml
"

docker cp spark/spark_streaming.py spark:/opt/bitnami/spark/spark_streaming.py

# Run the Spark streaming job
docker exec -it --user root spark /bin/bash -c "
  export HADOOP_HOME=/opt/hadoop-2.7.7 &&
  export PATH=\$PATH:\$HADOOP_HOME/bin &&
  spark-submit /opt/bitnami/spark/spark_streaming.py
"