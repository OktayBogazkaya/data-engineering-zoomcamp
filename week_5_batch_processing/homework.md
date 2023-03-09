## Week 5 Homework

In this homework we'll put what we learned about Spark in practice.

For this homework we will be using the FHVHV 2021-06 data found here. [FHVHV Data](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhvhv/fhvhv_tripdata_2021-06.csv.gz)

## Question 1: 

**Install Spark and PySpark** 

- Install Spark
- Run PySpark
- Create a local spark session
- Execute spark.version.

What's the output?
- 3.3.2
- 2.1.4
- 1.2.3
- 5.4
</br></br>

### Solution

>Answer:
```
3.3.2
```

## Question 2:

**HVFHW June 2021**

Read it with Spark using the same schema as we did in the lessons. 
We will use this dataset for all the remaining questions. 
Repartition it to 12 partitions and save it to parquet.
What is the average size of the Parquet (ending with .parquet extension) Files that were created (in MB)? Select the answer which most closely matches.

- 2MB
- 24MB
- 100MB
- 250MB

### Solution

``` python
#Import libs
import pyspark
from pyspark.sql import SparkSession
import pandas as pd
from pyspark.sql import types

#Start Spark Session
spark = SparkSession.builder \
    .master("local[*]") \
    .appName('test') \
    .getOrCreate()

#Download file
!wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhvhv/fhvhv_tripdata_2021-06.csv.gz

#Unzip file
%%sh
gunzip -d fhvhv_tripdata_2021-06.csv.gz

#Read csv file into pandas dataframe
df_pandas = pd.read_csv('fhvhv_tripdata_2021-06.csv')
#Check
df_pandas.dtypes

#Drop column 'Affiliated_base_number' to have the same schema mentioned in the question 2
df_pandas = df_pandas.drop('Affiliated_base_number', axis=1)
#Check 
df_pandas.dtypes

#Write new csv file without the 'Affiliated_base_number' column
df_pandas.to_csv('fhvhv_tripdata_2021-06.csv', index = False)

#Copy and build schema from previous lessons
schema = types.StructType([
    types.StructField('dispatching_base_num', types.StringType(), True),
    types.StructField('pickup_datetime', types.TimestampType(), True),
    types.StructField('dropoff_datetime', types.TimestampType(), True),
    types.StructField('PULocationID', types.IntegerType(), True),
    types.StructField('DOLocationID', types.IntegerType(), True),
    types.StructField('SR_Flag', types.StringType(), True)
    
])

#Read csv file into spark dataframe with the new schema
df = spark.read \
    .option("header", "true") \
    .schema(schema) \
    .csv('fhvhv_tripdata_2021-06.csv')

#Check
df.printSchema()

#Set Repartition and save it to parquet.
df = df.repartition(12)
df.write.parquet('fhvhv/2021/06/', mode='overwrite')

#Check
!ls -lh fhvhv/2021/06/
```

>Answer:
```
262MB
```

## Question 3: 

**Count records**  

How many taxi trips were there on June 15?</br></br>
Consider only trips that started on June 15.</br>

- 308,164
- 12,856
- 452,470
- 50,982
</br></br>

### Solution
``` python
#Read and register tempTable
df_fhvhv = spark.read.parquet('fhvhv/2021/06/')
df_fhvhv.registerTempTable('fhvhv_2021_06')

#SQL query
df_fhvhv = spark.sql("""
SELECT 
    COUNT(1)
FROM
    fhvhv_2021_06
WHERE
    to_date(pickup_datetime) = '2021-06-15'
""").show()
```

>Output:
```
452470
```

## Question 4: 

**Longest trip for each day**  

Now calculate the duration for each trip.</br>
How long was the longest trip in Hours?</br>

- 66.87 Hours
- 243.44 Hours
- 7.68 Hours
- 3.32 Hours
</br></br>

### Solution

``` python
df_fhvhv = spark.sql("""
SELECT 
    TIMESTAMPDIFF(hour, pickup_datetime,dropoff_datetime)
FROM
    fhvhv_2021_06
ORDER BY
    1 DESC
""").show()
```

>Output:
```
66 Hours
```

## Question 5: 

**User Interface**

 Spark’s User Interface which shows application's dashboard runs on which local port?</br>

- 80
- 443
- 4040
- 8080
</br></br>

### Solution

>Answer:
```
4040
```

## Question 6: 

**Most frequent pickup location zone**

Load the zone lookup data into a temp view in Spark</br>
[Zone Data](https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv)</br>

Using the zone lookup data and the fhvhv June 2021 data, what is the name of the most frequent pickup location zone?</br>

- East Chelsea
- Astoria
- Union Sq
- Crown Heights North
</br></br>

### Solution

``` python
#Load data
!wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv

#Read csv file into spark dataframe with 
df_zones = spark.read \
    .option("header", "true") \
    .csv('taxi_zone_lookup.csv')

#Check
df_zones.schema

# Create temporary view/table from the spark dataframe
df_zones.createOrReplaceTempView('zones')

#SQL query
spark.sql("""
SELECT 
    zones.Zone,
    Count(1)
FROM
    fhvhv_2021_06 f
    LEFT JOIN zones ON f.PULocationID = zones.LocationID
GROUP BY 
    1
ORDER BY 
    2 DESC
""").show()
```

>Answer:
```
Crown Heights North
```

## Submitting the solutions

* Form for submitting: https://forms.gle/EcSvDs6vp64gcGuD8
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 06 March (Monday), 22:00 CET


## Solution

We will publish the solution here
