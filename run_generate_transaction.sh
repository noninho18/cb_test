#!/bin/bash

# Start the Spark container if not already running
docker start spark || docker run -d --name spark bitnami/spark:latest

docker exec -it hadoop-namenode /bin/bash -c "
  hdfs dfsadmin -safemode leave
"
# Create the generator directory in the container if it doesn't exist
docker exec -it --user root spark mkdir -p /opt/bitnami/spark/generator

# Copy the Python script and requirements.txt to the Spark container
docker cp generator/generate_transaction.py spark:/opt/bitnami/spark/generator/generate_transaction.py
docker cp requirements.txt spark:/opt/bitnami/spark/generator/requirements.txt

# Set up virtual environment and install dependencies
docker exec -it --user root spark /bin/bash -c "
   cd /opt/bitnami/spark/generator &&
   python3 -m venv env &&
   source env/bin/activate &&
   pip install -r requirements.txt
"

# Execute the Python script inside the Spark container
docker exec -it --user root spark /bin/bash -c "
   source /opt/bitnami/spark/generator/env/bin/activate &&
   python3 /opt/bitnami/spark/generator/generate_transaction.py
"
