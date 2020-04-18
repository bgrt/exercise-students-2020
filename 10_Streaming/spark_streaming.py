#!/bin/python
#
# without Kafka
#spark-submit spark_streaming.py 



import os
import sys
import time
import datetime
import logging
import numpy as np
import socket
import re
from subprocess import check_output

from pyspark.mllib.linalg import Vectors
from pyspark.mllib.regression import LabeledPoint
from pyspark.mllib.clustering import StreamingKMeans
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode
from pyspark.sql.functions import split
from pyspark.sql.types import StructType
from pyspark.ml.feature import FeatureHasher
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator
from pyspark.ml import Pipeline
from pyspark.sql import functions as F

#######################################################################################
# CONFIGURATIONS
# Get current cluster setup from work directory
STREAMING_WINDOW=60

# Initialize PySpark
SPARK_MASTER="local[1]"
#SPARK_MASTER="spark://mpp3r03c04s06.cos.lrz.de:7077"
APP_NAME = "PySpark Lecture"
os.environ["PYSPARK_PYTHON"] = "/opt/tljh/user/bin/python"

# If there is no SparkSession, create the environment
try:
    sc and spark
except NameError as e:
    import pyspark
    import pyspark.sql
    conf=pyspark.SparkConf().set("spark.cores.max", "4")
    sc = pyspark.SparkContext(master=SPARK_MASTER, conf=conf)
    spark = pyspark.sql.SparkSession(sc).builder.appName(APP_NAME).getOrCreate()

print("PySpark initiated...") 


lines = spark \
        .readStream \
        .format("text") \
        .load(path="/opt/data/nasa/")

lines.printSchema()
print(type(lines))

words = lines \
    .filter(lines['value'].contains('- -')) \
    .select(
    explode(
        split(lines.value, ' ')
    ).alias('word')
)

wordCounts = words.groupBy('word').count()

# Start running the query that prints the running counts to the console
query = wordCounts \
    .writeStream \
    .outputMode('complete') \
    .format('console')\
    .start()

query.awaitTermination()
query.stop()
