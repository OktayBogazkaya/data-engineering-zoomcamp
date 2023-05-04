# Import necessary modules
from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials


@task(log_prints=True)
def extract_from_gcs():
    """Download data from GCS"""
    #gcs_path = f"data/reddit_{subreddit}_{year}-{month:02}-{day:02}.csv"
    gcs_block = GcsBucket.load("dezoomcamp-gcs")
    #print(f'The blobs in this folder are {gcs_block.list_blobs("data")}')
    blobs = gcs_block.list_blobs("data")
    home_Dir = Path.home()
    project_Dir = "data-engineering-zoomcamp/week_7_project"
    file_paths = [] 
    for key in blobs:
        print(key.name)
        # print(type(key.name))
        # print(Path(key.name))
        gcs_path = key.name
        gcs_block.get_directory(from_path=gcs_path, local_path=f'{home_Dir}/{project_Dir}')
        file_paths.append(Path(f'{home_Dir}/{project_Dir}/{key.name}'))
    
    return file_paths

    
@task(log_prints=True)
def transform(path):
    """Clean Data"""
    print(path)
    df = pd.read_csv(path, parse_dates=['created_utc'])
    print(df.head(2))
    print(df.info())
    print(f"pre: org not found count: {df['org'].value_counts()['No ticker found']}")
    df['org'] = df['org'].replace('No ticker found', '/')
    print(f"post: org not found count: {df['org'].value_counts().get('No ticker found',0)}")

    return df

@task()
def write_to_bq(df):
    """Write Data to BQ"""
    gcp_credentials_block = GcpCredentials.load("dezoomcamp-gcp-credentials")

    df.to_gbq(
        destination_table="reddit_dataset.wallstreetbets",
        project_id="constant-haven-384713",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000,
        if_exists="append",
    )

@flow()
def etl_gcs_to_bq():
    """Main ETL flow to load data into BigQuery"""

    file_paths = extract_from_gcs()
    for path in file_paths:
        df = transform(path)
        write_to_bq(df) 

if __name__ == '__main__':
    etl_gcs_to_bq()