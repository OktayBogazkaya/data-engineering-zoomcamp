## Week 2 Homework

Important Note:

You can load the data however you would like, but keep the files in .GZ Format. If you are using orchestration such as Airflow or Prefect do not load the data into Big Query using the orchestrator.
Stop with loading the files into a bucket.

NOTE: You can use the CSV option for the GZ files when creating an External Table

SETUP:
Create an **external table** using the fhv 2019 data.
Create a **table** in BQ using the fhv 2019 data (do not partition or cluster this table).
Data can be found here: https://github.com/DataTalksClub/nyc-tlc-data/releases/tag/fhv

## Question 1:
What is the count for fhv vehicle records for year 2019?

65,623,481
43,244,696
22,978,333
13,942,414

### Solution

Start Prefect Orion Server
```
prefect orion start
prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

Proposed changes in file **`etl_web_to_gcs_week3q1.py`**
``` python
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from random import randint


@task(retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into pandas DataFrame"""
    # if randint(0, 1) > 0:
    #     raise Exception

    df = pd.read_csv(dataset_url)
    return df

@task()
def write_local(df: pd.DataFrame, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    data_dir = 'data/fhv'
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    path = Path(f"data/fhv/{dataset_file}.csv.gz")
    df.to_csv(path, compression="gzip")
    return path


@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    return


@flow()
def etl_web_to_gcs(year: int, month: int) -> None:
    """The main ETL function"""

    dataset_file = f"fhv_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/{dataset_file}.csv.gz"
    df = fetch(dataset_url)
    path = write_local(df, dataset_file)
    write_gcs(path)


@flow()
def etl_parent_flow(
    months: list[int] = [1, 2], year: int = 2021
):
    for month in months:
        etl_web_to_gcs(year, month)


if __name__ == "__main__":
    months = list(range(1,13))
    year = 2019
    etl_parent_flow(months, year)

```

Run ETL script from terminal
```
python etl_web_to_gcs_week3q1.py
```

Check if all files are succesfully downloaded to GCP

![Bildschirmfoto 2023-02-14 um 18 29 03](https://user-images.githubusercontent.com/104417609/218813028-5a11f1ae-2bbc-422b-a7e9-d80c97c6bd89.png)

Go to BQ and and create table `fhv_tripdata_2019` using the fhv 2019 data without partition or cluster

![Bildschirmfoto 2023-02-14 um 19 20 29](https://user-images.githubusercontent.com/104417609/218824210-28ff705a-0e96-4ec3-ad98-a49809d93e42.png)

Create external table using the fhv 2019 data

Proposed query: 
``` sql
CREATE OR REPLACE EXTERNAL TABLE `gentle-presence-375809.dezoomcamp.external_fhv_tripdata_2019`
OPTIONS (
  format = 'CSV', 
  uris  = ['gs://prefect-de-zoomcamp2023/data/fhv/fhv_tripdata_2019-*.csv.gz']
);
```

Run following query to count for fhv vehicle records in 2019

Proposed query: 
``` sql
SELECT Count(*) FROM gentle-presence-375809.dezoomcamp.external_fhv_tripdata_2019 
``` 

>Output:
```
43,244,696
```

## Question 2:

Write a query to count the distinct number of affiliated_base_number for the entire dataset on **both the tables**.
What is the estimated amount of data that will be read when this query is executed on the **External Table** and **the Table**?

25.2 MB for the External Table and 100.87MB for the BQ Table
225.82 MB for the External Table and 47.60MB for the BQ Table
0 MB for the External Table and 0MB for the BQ Table
0 MB for the External Table and 317.94MB for the BQ Table

### Solution

Proposed query from external table:
``` sql
SELECT COUNT(DISTINCT(affiliated_base_number)) FROM `gentle-presence-375809.dezoomcamp.external_fhv_tripdata_2019`; 
```
Proposed query from BQ table:
``` sql
SELECT COUNT(DISTINCT(affiliated_base_number)) FROM `gentle-presence-375809.dezoomcamp.fhv_tripdata_2019`; 
```

>Answer:
```
0 MB for external table and 317.94 MB for BQ table
```

## Question 3: 

How many records have both a blank (null) PUlocationID and DOlocationID in the entire dataset?

* 717,748
* 1,215,687
* 5
* 20,332

### Solution

Proposed query:
``` sql
SELECT COUNT(*) FROM `gentle-presence-375809.dezoomcamp.fhv_tripdata_2019` 
WHERE PUlocationID is null AND DOlocationID is null; 
```

>Output:
```
717,748
```

## Question 4:

What is the best strategy to optimize the table if query always filter by pickup_datetime and order by affiliated_base_number?

Cluster on pickup_datetime Cluster on affiliated_base_number
Partition by pickup_datetime Cluster on affiliated_base_number
Partition by pickup_datetime Partition by affiliated_base_number
Partition by affiliated_base_number Cluster on pickup_datetime

### Solution

>Answer:
```
Partition by pickup_datetime Cluster on affiliated_base_number
```

## Question 5:
Implement the optimized solution you chose for question 4. Write a query to retrieve the distinct affiliated_base_number between pickup_datetime 2019/03/01 and 2019/03/31 (inclusive).
Use the BQ table you created earlier in your from clause and note the estimated bytes. Now change the table in the from clause to the partitioned table you created for question 4 and note the estimated bytes processed. What are these values? Choose the answer which most closely matches.

12.82 MB for non-partitioned table and 647.87 MB for the partitioned table
647.87 MB for non-partitioned table and 23.06 MB for the partitioned table
582.63 MB for non-partitioned table and 0 MB for the partitioned table
646.25 MB for non-partitioned table and 646.25 MB for the partitioned table

### Solution

Proposed query for implementation of optimized solution **Partition by pickup_datetime Cluster on affiliated_base_number**
``` sql
CREATE OR REPLACE TABLE `gentle-presence-375809.dezoomcamp.external_fhv_tripdata_2019_partitoned_clustered`
PARTITION BY DATE(pickup_datetime)
CLUSTER BY affiliated_base_number AS
SELECT * FROM gentle-presence-375809.dezoomcamp.fhv_tripdata_2019;
```

Proposed query for non-partitoned_clustered table:
``` sql
SELECT DISTINCT(affiliated_base_number) 
FROM gentle-presence-375809.dezoomcamp.fhv_tripdata_2019
WHERE (DATE(pickup_datetime) >= '2019-03-01' AND DATE(pickup_datetime) <= '2019-03-31')
``` 
![Bildschirmfoto 2023-02-15 um 11 02 55](https://user-images.githubusercontent.com/104417609/218996595-27e0cff3-d959-4d93-b177-23b16080af75.png)

Proposed query for partitoned_clustered table:
``` sql
SELECT DISTINCT(affiliated_base_number) 
FROM gentle-presence-375809.dezoomcamp.external_fhv_tripdata_2019_partitoned_clustered
WHERE (DATE(pickup_datetime) >= '2019-03-01' AND DATE(pickup_datetime) <= '2019-03-31')
```
![Bildschirmfoto 2023-02-15 um 11 05 11](https://user-images.githubusercontent.com/104417609/218997087-9d8838e8-9b11-482f-9829-b5d542835f26.png)

>Asnwer:
```
647.87 MB for non-partitioned table and 23.06 MB for the partitioned table
```

## Question 6:
Where is the data stored in the External Table you created?

* Big Query
* GCP Bucket
* Container Registry
* Big Table

### Solution

>Answer:
```
GCP Bucket
```

## Question 7:
It is best practice in Big Query to always cluster your data:

* True
* False

### Solution

>Answer:
```
False
```

## (Not required) Question 8:
A better format to store these files may be parquet. Create a data pipeline to download the gzip files and convert them into parquet. Upload the files to your GCP Bucket and create an External and BQ Table.

Note: Column types for all files used in an External Table must have the same datatype. While an External Table may be created and shown in the side panel in Big Query, this will need to be validated by running a count query on the External Table to check if any errors occur.


## Submitting the solutions

* Form for submitting: https://forms.gle/rLdvQW2igsAT73HTA
* You can submit your homework multiple times. In this case, only the last submission will be used.

Deadline: 13 February (Monday), 22:00 CET

## Solution

We will publish the solution here
