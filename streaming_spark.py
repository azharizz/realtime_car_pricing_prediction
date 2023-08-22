
import os
os.environ['PYSPARK_SUBMIT_ARGS'] = '--packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.2.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 pyspark-shell'

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/azhar_elbachtiar/debez/project-azhar-396703-47fe772d51fc.json"

from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

from google.cloud import storage
import pandas as pd
import requests

# Create a Spark session
spark = SparkSession.builder \
    .appName("KafkaStreamReader") \
    .getOrCreate()

# Define the Kafka broker and topic
kafka_broker = "localhost:9092"  # Replace with your Kafka broker address
kafka_topic = "dbserver1.inventory.car_products"  # Replace with your Kafka topic

# Define the options for reading from Kafka
kafka_options = {
    "kafka.bootstrap.servers": kafka_broker,
    "subscribe": kafka_topic
}


# Read data from Kafka using readStream
df = spark.readStream \
    .format("kafka") \
    .options(**kafka_options) \
    .load()

# You can process the data here using DataFrame operations
# For example, you can select the key and value columns
#processed_df = df.selectExpr("key", "value")

print('Starting to data transformation...')

schema = StructType([
    StructField("schema", StringType(), nullable=False),
    StructField("payload", StringType(), nullable=False)
])

df = df.selectExpr("CAST(value AS STRING)")
df = df.select(from_json(df.value, schema).alias("parsed_data")).select("parsed_data.*")


schema = StructType([
    StructField("after", StringType(), nullable=True)
])


df = df.selectExpr("CAST(payload AS STRING)")
df = df.select(from_json(df.payload, schema).alias("data")).select("data.*")



schema = StructType([
    StructField("car_ID", IntegerType(), nullable=True),
    StructField("CarName", StringType(), nullable=True),
    StructField("fueltype", StringType(), nullable=True),
    StructField("carlength", DoubleType(), nullable=True),
    StructField("carwidth", DoubleType(), nullable=True),
    StructField("carheight", DoubleType(), nullable=True),
    StructField("enginesize", IntegerType(), nullable=True),
    StructField("peakrpm", IntegerType(), nullable=True),
])

df = df.selectExpr("CAST(after AS STRING)")
df = df.select(from_json(df.after, schema).alias("data")).select("data.*")


print('Finished data transformation...')

processed_df = df





def write_to_gcs(df,epoch_id):

    # local_output_path = "output.csv"
    # gs_output_path = "checkpoint"

    print("MODEL PREDICT")
    print("================================================================================================")
    
    
    df_pd = df.toPandas()
    
    print(df_pd)
    
    if df_pd['car_ID'].isnull().values.any() == False and (len(df_pd) > 0):

        # Convert the dataframe into dictionary
        dict_df = df_pd.to_dict(orient='list')
        
        input_data = {
                "car_ID": dict_df['car_ID'][0],
                "CarName": dict_df['CarName'][0],
                "fueltype": dict_df['fueltype'][0],
                "carlength": dict_df['carlength'][0],
                "carwidth": dict_df['carwidth'][0],
                "carheight": dict_df['carheight'][0],
                "enginesize": dict_df['enginesize'][0],
                "peakrpm": dict_df['peakrpm'][0]
            }
        

        print('Trying to predict data...')
        

        response = requests.post("http://localhost:8000/predict/", json=input_data)
        
        prediction = response.json()["prediction"]
        
        print('Success to predict data...')
        
        print(prediction)
        
        df_pred = pd.DataFrame(prediction)
        
        print('Success transform the prediction')
        
        
        print(df_pred)
        
        print(dict_df)
        
        print('Insert into Cloud Storage..')
        client = storage.Client()
        bucket = client.get_bucket('staging_to_bq_azhar')
        
        bucket.blob('staging_prediction.csv').upload_from_string(df_pred.to_csv(index=False), 'text/csv')
        
        print('Success inserted')
        
    else:
        print("Data is invalid...")
    
    
    
# Define the query for processing the stream
query = processed_df.writeStream \
    .foreachBatch(write_to_gcs) \
    .start()

# Wait for the query to terminate
query.awaitTermination()
