## Week 2 Homework

The goal of this homework is to familiarise users with workflow orchestration and observation. 

## Question 1. Load January 2020 data

Using the `etl_web_to_gcs.py` flow that loads taxi data into GCS as a guide, create a flow that loads the green taxi CSV dataset for January 2020 into GCS and run it. Look at the logs to find out how many rows the dataset has.

How many rows does that dataset have?

* 447,770
* 766,792
* 299,234
* 822,132

### Solution

Based on the info in [data dictionary](https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_green.pdf) the date column names need to be changed 

![image](https://user-images.githubusercontent.com/104417609/217062331-453e303e-8b6b-4738-b442-6eb68dce9dd6.png)

Proposed changes in file **`etl_web_to_gcs.py`**
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

@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
    df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    return df

@task()
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    data_dir = f'data/{color}'
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    path = Path(f"data/{color}/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    return

@flow()
def etl_web_to_gcs() -> None:
    """The main ETL function"""
    
    # Initial parameters
    # color = "yellow"
    #year = 2021
    #month = 1

    # Parameters for homework 2 question 1
    color = "green"
    year = 2020
    month = 1
    
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"
    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)

if __name__ == "__main__":
    etl_web_to_gcs()
```
Start Prefect Orion Server
```
prefect orion start
```

Run ETL script from terminal
```
python flows/02_gcp/etl_web_to_gcs.py
```

>Output:
```
447,770
```

## Question 2. Scheduling with Cron

Cron is a common scheduling specification for workflows. 

Using the flow in `etl_web_to_gcs.py`, create a deployment to run on the first of every month at 5am UTC. What’s the cron schedule for that?

- `0 5 1 * *`
- `0 0 5 1 *`
- `5 * 1 0 *`
- `* * 5 1 0`

### Solution

Go to https://crontab.guru/ and check the right cron schedule based on the given options

![image](https://user-images.githubusercontent.com/104417609/217064808-34316a11-2f8c-4b6d-af2b-8423df673a8a.png)

Build and run workflow :
```
prefect deployment build flows/02_gcp/etl_web_to_gcs.py:etl_web_to_gcs -n "ETL HomeworkWeek2Q2" --cron "0 5 1 * *"
```

Check in Prefect Orion UI wheter the scheduled deployment worked

![image](https://user-images.githubusercontent.com/104417609/217181777-9de34ed8-1e8e-4966-8267-919e3aecfe3b.png)

>Output:
```
`0 5 1 * *`
```

## Question 3. Loading data to BigQuery 

Using `etl_gcs_to_bq.py` as a starting point, modify the script for extracting data from GCS and loading it into BigQuery. This new script should not fill or remove rows with missing values. (The script is really just doing the E and L parts of ETL).

The main flow should print the total number of rows processed by the script. Set the flow decorator to log the print statement.

Parametrize the entrypoint flow to accept a list of months, a year, and a taxi color. 

Make any other necessary changes to the code for it to function as required.

Create a deployment for this flow to run in a local subprocess with local flow code storage (the defaults).

Make sure you have the parquet data files for Yellow taxi data for Feb. 2019 and March 2019 loaded in GCS. Run your deployment to append this data to your BiqQuery table. How many rows did your flow code process?

- 14,851,920
- 12,282,990
- 27,235,753
- 11,338,483

### Solution

Get Feb and March 2019 yellow taxi data and upload to GCS 

Proposed changes in file **`parameterized_flow.py'**
``` python
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from random import randint
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(retries=3)
def fetch(dataset_url: str) -> pd.DataFrame:
    """Read taxi data from web into pandas DataFrame"""
    # if randint(0, 1) > 0:
    #     raise Exception
    df = pd.read_csv(dataset_url)
    return df

@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    df["tpep_pickup_datetime"] = pd.to_datetime(df["tpep_pickup_datetime"])
    df["tpep_dropoff_datetime"] = pd.to_datetime(df["tpep_dropoff_datetime"])
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    return df

@task()
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    data_dir = f'data/{color}'
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    path = Path(f"data/{color}/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    return
@flow()
def etl_web_to_gcs(year: int, month: int, color: str) -> None:
    """The main ETL function"""
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"
    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)

@flow()
def etl_parent_flow(
    months: list[int] = [1, 2], year: int = 2021, color: str = "yellow"
):
    for month in months:
        etl_web_to_gcs(year, month, color)

if __name__ == "__main__":
    color = "yellow"
    months = [2, 3]
    year = 2019
    etl_parent_flow(months, year, color)
```

Check if Feb and March 2019 data is successfully uploaded to GCS

![image](https://user-images.githubusercontent.com/104417609/217183059-125c2cfb-fe1a-445f-be64-ac8c4e1415b6.png)

Proposed changes in file **`etl_gcs_to_bq_homework2q3.py'**
```python
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@task(retries=3)
def extract_from_gcs(color: str, year: int, month: int) -> Path:
    """Download trip data from GCS"""
    gcs_path = f"data/{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"../data/")
    return Path(f"../data/{gcs_path}")

@task()
def read(path: Path) -> pd.DataFrame:
    """Data cleaning example"""
    df = pd.read_parquet(path)
    #print(f"pre: missing passenger count: {df['passenger_count'].isna().sum()}")
    #df["passenger_count"].fillna(0, inplace=True)
    #print(f"post: missing passenger count: {df['passenger_count'].isna().sum()}")
    return df

@task()
def write_bq(df: pd.DataFrame) -> None:
    """Write DataFrame to BiqQuery"""
    gcp_credentials_block = GcpCredentials.load("zoom-gcp-creds")
    df.to_gbq(
        destination_table="dezoomcamp.rides",
        project_id="gentle-presence-375809",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )

@flow()
def etl_gcs_to_bq(year: int, month: int, color: str) -> int:
    """Main ETL flow to load data into Big Query"""
    path = extract_from_gcs(color, year, month)
    df = read(path)
    write_bq(df)
    return df
@flow(log_prints=True)
def etl_parent_flow(
    months: list[int] = [2, 3], year: int = 2019, color: str = "yellow"
):
    total_rows = 0
    for month in months:
        df = etl_gcs_to_bq(year, month, color)
        total_rows += len(df)
    print(f"Total number of rows processed {total_rows}")

if __name__ == "__main__":
    color = "yellow"
    months = [2, 3]
    year = 2019
    etl_parent_flow(months, year, color)
```

Create deployment for this flow
```
prefect deployment build flows/02_gcp/etl_gcs_to_bq_homework2q3.py:etl_parent_flow -n HomeworkWeek2Q3 -a
```

Start agent
```
prefect agent start -q 'default'
```

Go to Prefect Orion UI and start Quick run

![image](https://user-images.githubusercontent.com/104417609/217185911-d8b236db-7f16-4c95-9704-f68389e7d684.png)

Go to log of the main flow run and check the printed statement

![image](https://user-images.githubusercontent.com/104417609/217185992-b6fe4e81-eac9-40ef-b9c7-a3af2ddca60b.png)


>Output:
```
14,851,920
```

## Question 4. Github Storage Block

Using the `web_to_gcs` script from the videos as a guide, you want to store your flow code in a GitHub repository for collaboration with your team. Prefect can look in the GitHub repo to find your flow code and read it. Create a GitHub storage block from the UI or in Python code and use that in your Deployment instead of storing your flow code locally or baking your flow code into a Docker image. 

Note that you will have to push your code to GitHub, Prefect will not push it for you.

Run your deployment in a local subprocess (the default if you don’t specify an infrastructure). Use the Green taxi data for the month of November 2020.

How many rows were processed by the script?

- 88,019
- 192,297
- 88,605
- 190,225

### Solution

Get Nov 2020 green taxi data and upload to GCS

Proposed changes in file **`etl_web_to_gcs_homework2q4.py'**
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

@task(log_prints=True)
def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fix dtype issues"""
    df["lpep_pickup_datetime"] = pd.to_datetime(df["lpep_pickup_datetime"])
    df["lpep_dropoff_datetime"] = pd.to_datetime(df["lpep_dropoff_datetime"])
    print(df.head(2))
    print(f"columns: {df.dtypes}")
    print(f"rows: {len(df)}")
    return df

@task()
def write_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    """Write DataFrame out locally as parquet file"""
    data_dir = f'data/{color}'
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    path = Path(f"data/{color}/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path

@task()
def write_gcs(path: Path) -> None:
    """Upload local parquet file to GCS"""
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.upload_from_path(from_path=path, to_path=path)
    return

@flow()
def etl_web_to_gcs() -> None:
    """The main ETL function"""
    
    # Initial parameters
    # color = "yellow"
    #year = 2021
    #month = 1
    
    # Parameters for homework 2 question 1
    color = "green"
    year = 2020
    month = 11
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"
    df = fetch(dataset_url)
    df_clean = clean(df)
    path = write_local(df_clean, color, dataset_file)
    write_gcs(path)

if __name__ == "__main__":
    etl_web_to_gcs()
```

Create Github block in Prefect Orion UI

![image](https://user-images.githubusercontent.com/104417609/217186508-9f3e32b5-7937-4574-acab-c4708d5ff09e.png)

Upload __'etl_web_to_gcs_homework2q4.py'__ to Github repo and clone the repo to local machine (good discussion about this step in [de-zoomcamp slack channel](https://datatalks-club.slack.com/archives/C01FABYF2RG/p1675687541144979?thread_ts=1675196079.892889&cid=C01FABYF2RG)
```
$ git clone <repo-url>
```

Run build deployment from the git root folder on local machine
```
prefect deployment build ./week_2_workflow_orchestration/homework/etl_web_to_gcs_homework2q4.py:etl_web_to_gcs -n "HomeworkWeek2Q4 Github Storage Flow" -sb github/github-block -a
```

Start agent
```
prefect agent start -q 'default'
```

Go to Prefect Orion UI > Deployments > Select the "...GitHub Storage Flow" deployment and start Quick run

![image](https://user-images.githubusercontent.com/104417609/217191112-246d43a4-48cf-47d1-99e8-b7cde42ddfd3.png)

>Output:
```
88,605
```

## Question 5. Email or Slack notifications

Q5. It’s often helpful to be notified when something with your dataflow doesn’t work as planned. Choose one of the options below for creating email or slack notifications.

The hosted Prefect Cloud lets you avoid running your own server and has Automations that allow you to get notifications when certain events occur or don’t occur. 

Create a free forever Prefect Cloud account at app.prefect.cloud and connect your workspace to it following the steps in the UI when you sign up. 

Set up an Automation that will send yourself an email when a flow run completes. Run the deployment used in Q4 for the Green taxi data for April 2019. Check your email to see the notification.

Alternatively, use a Prefect Cloud Automation or a self-hosted Orion server Notification to get notifications in a Slack workspace via an incoming webhook. 

Join my temporary Slack workspace with [this link](https://join.slack.com/t/temp-notify/shared_invite/zt-1odklt4wh-hH~b89HN8MjMrPGEaOlxIw). 400 people can use this link and it expires in 90 days. 

In the Prefect Cloud UI create an [Automation](https://docs.prefect.io/ui/automations) or in the Prefect Orion UI create a [Notification](https://docs.prefect.io/ui/notifications/) to send a Slack message when a flow run enters a Completed state. Here is the Webhook URL to use: https://hooks.slack.com/services/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

Test the functionality.

Alternatively, you can grab the webhook URL from your own Slack workspace and Slack App that you create. 


How many rows were processed by the script?

- `125,268`
- `377,922`
- `728,390`
- `514,392`

### Solution

Go to https://www.prefect.io/pricing/ > Create Prefect Cloud account > Create a workspace > Create API-Key > log-in form terminal
```
prefect cloud login -k <API-Key>
```

Build and deploy flow
```
prefect deployment build ./etl_web_to_gcs.py:etl_web_to_gcs -n "Prefect Cloud Flow" -a
```

Create email block from Prefect Cloud UI

![image](https://user-images.githubusercontent.com/104417609/217192503-49508306-b773-46b4-8cb0-9d02c4a18902.png)

Go To Prefect Cloud UI > Select Automations > Create trigger and actions

![image](https://user-images.githubusercontent.com/104417609/217193332-b7783fb6-46b7-46f4-8d85-a0d9c2b1ea7f.png)

![image](https://user-images.githubusercontent.com/104417609/217193356-ee9a5c82-9a6e-4424-b929-139f4e97faae.png)


Run delpoyed flow 
```
prefect deployment run "etl-web-to-gcs/Prefect Cloud Flow"
```

Start agent
```
prefect agent start --work-queue "default"
```

>Output:
```
514,392
```

## Question 6. Secrets

Prefect Secret blocks provide secure, encrypted storage in the database and obfuscation in the UI. Create a secret block in the UI that stores a fake 10-digit password to connect to a third-party service. Once you’ve created your block in the UI, how many characters are shown as asterisks (*) on the next page of the UI?

- 5
- 6
- 8
- 10

### Solution

Go to Prefect Cloud UI > Block > Choose Secret and create

![image](https://user-images.githubusercontent.com/104417609/217194867-5c78142e-be22-4e5f-a80c-0ada6d3b3707.png)

>Answer:
```
8
```

## Submitting the solutions

* Form for submitting: https://forms.gle/PY8mBEGXJ1RvmTM97
* You can submit your homework multiple times. In this case, only the last submission will be used. 

Deadline: 8 February (Wednesday), 22:00 CET


## Solution

We will publish the solution here
