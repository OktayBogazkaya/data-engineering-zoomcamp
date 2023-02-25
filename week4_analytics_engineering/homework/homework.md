## Week 4 Homework

In this homework, we'll use the models developed during the week 4 videos and enhance the already presented dbt project using the already loaded Taxi data for fhv vehicles for year 2019 in our DWH.

This means that in this homework we use the following data [Datasets list](https://github.com/DataTalksClub/nyc-tlc-data/)
* Yellow taxi data - Years 2019 and 2020
* Green taxi data - Years 2019 and 2020 
* fhv data - Year 2019. 

We will use the data loaded for:

* Building a source table: `stg_fhv_tripdata`
* Building a fact table: `fact_fhv_trips`
* Create a dashboard 

If you don't have access to GCP, you can do this locally using the ingested data from your Postgres database
instead. If you have access to GCP, you don't need to do it for local Postgres -
only if you want to.

> **Note**: if your answer doesn't match exactly, select the closest option 

## Question 1:
**What is the count of records in the model fact_trips after running all models with the test run variable disabled and filtering for 2019 and 2020 data only (pickup datetime)?** 

You'll need to have completed the ["Build the first dbt models"](https://www.youtube.com/watch?v=UVI30Vxzd6c) video and have been able to run the models via the CLI. 
You should find the views and models for querying in your DWH.

- 41648442
- 51648442
- 61648442
- 71648442

### Solution

Proposed query in BQ:
``` sql
SELECT count(*) FROM `gentle-presence-375809.production.fact_trips` WHERE EXTRACT(year FROM pickup_datetime) in (2019,2020) 
```

>Output:
```
61648442
```

<img width="953" alt="Bildschirmfoto 2023-02-25 um 07 49 00" src="https://user-images.githubusercontent.com/104417609/221343156-ce00b8b1-578f-4373-b953-52cecf6645f6.png">

## Question 2:

**What is the distribution between service type filtering by years 2019 and 2020 data as done in the videos?**

You will need to complete "Visualising the data" videos, either using [google data studio](https://www.youtube.com/watch?v=39nLTs74A3E) or [metabase](https://www.youtube.com/watch?v=BnLkrA7a6gM). 

- 89.9/10.1
- 94/6
- 76.3/23.7
- 99.1/0.9

### Solution

>Answer:
```
89.9/10.1 (89,8% Yellow / 10,2% Green)
```
<img width="925" alt="Bildschirmfoto 2023-02-25 um 07 55 11" src="https://user-images.githubusercontent.com/104417609/221362847-197735e9-0baf-4d82-8377-40d04fa14327.png">

## Question 3: 

**What is the count of records in the model stg_fhv_tripdata after running all models with the test run variable disabled (:false)?**  

Create a staging model for the fhv data for 2019 and do not add a deduplication step. Run it via the CLI without limits (is_test_run: false).
Filter records with pickup time in year 2019.

- 33244696
- 43244696
- 53244696
- 63244696

### Solution

Proposed query for **staging_fhv_tripdata_2019.sql**
``` sql
{{ config(materialized='view') }}

select 

    cast(PUlocationID as integer) as pickup_locationid,
    cast(DOlocationID as integer) as dropoff_locationid,
    
    -- timestamps
    cast(pickup_datetime as timestamp) as pickup_datetime,
    cast(dropOff_datetime as timestamp) as dropoff_datetime

from {{ source('staging','fhv_tripdata_2019') }}

-- dbt build --m <model.sql> --var 'is_test_run: false'
--{% if var('is_test_run', default=true) %}

--  limit 100

--{% endif %}
```

Proposed query in BQ:
``` sql
SELECT count(*) FROM `gentle-presence-375809.dbt_obogazkaya.staging_fhv_tripdata_2019` WHERE EXTRACT(year FROM pickup_datetime) = 2019 
```

>Output:
```
43244696
```

## Question 4:

**What is the count of records in the model fact_fhv_trips after running all dependencies with the test run variable disabled (:false)?**  

Create a core model for the stg_fhv_tripdata joining with dim_zones.
Similar to what we've done in fact_trips, keep only records with known pickup and dropoff locations entries for pickup and dropoff locations. 
Run it via the CLI without limits (is_test_run: false) and filter records with pickup time in year 2019.

- 12998722
- 22998722
- 32998722
- 42998722

### Solution

Proposed query for **fact_fhv_trips.sql**
``` sql
{{ config(materialized='table') }}

with fhv_data as (
    select * from {{ ref('staging_fhv_tripdata_2019') }}
), 

dim_zones as (
    select * from {{ ref('dim_zones') }}
    where borough != 'Unknown'
)

select 
    fhv_data.pickup_locationid, 
    pickup_zone.borough as pickup_borough, 
    pickup_zone.zone as pickup_zone, 
    fhv_data.dropoff_locationid,
    dropoff_zone.borough as dropoff_borough, 
    dropoff_zone.zone as dropoff_zone,  
    fhv_data.pickup_datetime, 
    fhv_data.dropoff_datetime
from fhv_data
inner join dim_zones as pickup_zone
on fhv_data.pickup_locationid = pickup_zone.locationid
inner join dim_zones as dropoff_zone
on fhv_data.dropoff_locationid = dropoff_zone.locationid
```

Proposed query in BQ:
``` sql
SELECT Count(*) FROM `gentle-presence-375809.production.fact_fhv_trips` WHERE EXTRACT(year FROM pickup_datetime) = 2019 
```

>Output:
```
22998722
```

## Question 5:

**What is the month with the biggest amount of rides after building a tile for the fact_fhv_trips table?**

Create a dashboard with some tiles that you find interesting to explore the data. One tile should show the amount of trips per month, as done in the videos for fact_trips, based on the fact_fhv_trips table.

- March
- April
- January
- December

### Solution

>Answer:
```
January
```

<img width="1431" alt="Bildschirmfoto 2023-02-25 um 16 50 40" src="https://user-images.githubusercontent.com/104417609/221366449-40f7f3e9-837e-4d01-971a-0c44042bf193.png">


## Submitting the solutions

* Form for submitting: https://forms.gle/6A94GPutZJTuT5Y16
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 25 February (Saturday), 22:00 CET


## Solution

We will publish the solution here
