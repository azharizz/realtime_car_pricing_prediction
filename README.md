# **Realtime Car Pricing Prediction**

## **Note: In Free Trial GCP, cannot inject from spark to bigquery in streaming mode. So i make alternatives using Google Cloud Functions to make it streaming mode**


For Detail Information on : https://azharizz.my.canva.site/

OR

Visit this Youtube Video :
https://youtu.be/mvJR-IZ9x04
<a href="https://youtu.be/mvJR-IZ9x04" target="_blank">
 <img src="https://img.youtube.com/vi/mvJR-IZ9x04/maxresdefault.jpg" alt="Watch the video" width="720" height="480" border="10" />
</a>



Note Step for Azhar:

Step 1
```
https://docs.docker.com/engine/install/debian/
```

Step 2
```
https://debezium.io/documentation/reference/stable/tutorial.html#considerations-running-debezium-docker

docker run -it --rm --name zookeeper -p 2181:2181 -p 2888:2888 -p 3888:3888 quay.io/debezium/zookeeper:2.3
```

step 3 inject .sql

step 4
```
docker run -it --rm --name connect -p 8083:8083 -e GROUP_ID=1 -e CONFIG_STORAGE_TOPIC=my_connect_configs -e OFFSET_STORAGE_TOPIC=my_connect_offsets -e STATUS_STORAGE_TOPIC=my_connect_statuses --link kafka:kafka --link mysql:mysql quay.io/debezium/connect:2.3
```

step 5
```
curl -H "Accept:application/json" localhost:8083/
curl -H "Accept:application/json" localhost:8083/connectors/
```

step 6
```
curl -i -X POST -H "Accept:application/json" -H "Content-Type:application/json" localhost:8083/connectors/ -d '{ "name": "inventory-connector", "config": { "connector.class": "io.debezium.connector.mysql.MySqlConnector", "tasks.max": "1", "database.hostname": "mysql", "database.port": "3306", "database.user": "debezium", "database.password": "dbz", "database.server.id": "184054", "topic.prefix": "dbserver1", "database.include.list": "inventory", "schema.history.internal.kafka.bootstrap.servers": "kafka:9092", "schema.history.internal.kafka.topic": "schemahistory.inventory" } }'
```

step 7
```
curl -i -X GET -H "Accept:application/json" localhost:8083/connectors/inventory-connector
```

step 8 
```
docker run -it --rm --name watcher --link zookeeper:zookeeper --link kafka:kafka quay.io/debezium/kafka:2.3 watch-topic -a -k dbserver1.inventory.car_products
```

step 9
```
apt-get install pip
pip install pyspark
sudo apt-get install openjdk-11-jdk


optional:
vi ~/.bashrc
export JAVA_HOME=(Path to the JDK, e.x: /usr/lib/jvm/java-11-openjdk-amd64)
source ~/.bashrc
```


step 10 
Install Fast API 
```
docker build -t fast_api_model .
docker compose up
```

step 11
run pyspark with python3 and install dependencies
note: 
To reduce cost time running this bash and im not used docker.
```
python3 streaming_spark.py
```
