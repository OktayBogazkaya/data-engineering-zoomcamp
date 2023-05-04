# Data Engineering Zoomcamp 2023 Project

This folder contains my final project for the completion of the Data Engineering Zoomcamp 2023 Cohort by [DataTalks.Club](https://datatalks.club/)

# Data Engineering Zoomcamp 2023 Project

This folder contains my final project for the completion of the Data Engineering Zoomcamp 2023 Cohort by [DataTalks.Club](https://datatalks.club/)

## Table of Contents

- [Problem Statement](#problem-statement)
- [Dataset](#dataset)
- [Technologies](#technologies)
- [Architecture](#architecture)
- [Dashboard](#dashboard)
- [Getting Started/Reproducibility](#getting-startedreproducibility)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Acknowledgements](#acknowledgements)

## Problem Statement

Social media has become an essential part of our lives, and it has revolutionized the way people interact and share information. [Reddit](https://www.reddit.com/) is one of the most popular soical media platforms with a vast user base and the availability of diverse online communuties (called **subreddits**) on a wide range of topics.
In particular, the subreddit [r/wallstreetbets](https://www.reddit.com/r/wallstreetbets) has gained a lot of attention due to its discussions about stock market trends and investment strategies where investors and traders hang out regularly. It therefore provides a wealth of data that can be used to extract valuable insights into market trends and investor behavior.

The goal of this project is to apply everything we learned in this course and build an end-to-end data pipeline. The Reddit API is used to extract data and build a dashboard that will enable end users to easily visualize and analyze the trends in investor behavior and market sentiment.

The current implementation of the project helps to analyze the title of a given reddit post to determine whether it has a positive, negative, or neutral sentiment using one of the Python libs called [NLTK](https://www.nltk.org/), and also identifies any organization mentioned in the title by making use of [SpaCy](https://spacy.io/) which is another lib for advanced NLP in Python. 

There are several ways that this project could be expanded upon in the future. For example, the accuracy of the sentiment analysis can be improved by using a more advanced model or finetuning pre-trained model with custom dat from various sources. Also the NER capabilities can be extended to recognize other types of entities besides organizations. 

## Dataset

The dataset for this project is sourced from the **r/wallstreetbets** subreddit using the Python Reddit API Wrapper [PRAW](https://praw.readthedocs.io/en/stable/index.html). The dataset includes submissions, comments, and other interactions related to stocks and investment trends. The data pipeline will run daily to ensure that the data is up-to-date and reflects the latest trends and insights from the subreddit.

## Technologies

- Data - [Reddit API](https://www.reddit.com/dev/api/)
- Cloud - [Google Cloud Platform](https://cloud.google.com/)
- Data Lake - [Google Cloud Storage](https://cloud.google.com/storage)
- DWH - [BigQuery](https://cloud.google.com/bigquery)
- Infrastructure-as-Code (IaC) - [Terraform](https://www.terraform.io/)
- Workflow Orchestration - [Prefect](https://www.prefect.io/)
- Visualisation - [Looker Studio](https://datastudio.google.com/)

## Architecture 

![DE Zoomcamp Project Architecture](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]de_zoomcamp_project_architecture.png?raw=true)

## Dashboard 

Looker Studio is used to build the dashboard which pulls data from the BQ table.

Link to the dashboard: https://lookerstudio.google.com/datasources/dc888e97-5a6b-4de1-bb8a-86c5c49468aa

This is the first MVP and gives an overview of the daily discussions in the WallStreetBet subreddit with main focus on stock market and and sentiment analysis. As this projects develops, new KPI's will be added in the future. 

![MVP Dashboard DEZoomcamp Project](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]MVP_Dashboard_DEZoomcamp_Project.png?raw=true)

## Getting Started/Reproducibility

This section contains the steps you need to follow to reproduce the project results. First, make sure to follow all the steps in [presteps](data-engineering-zoomcamp/week_7_project/presteps.md) for seting up the VM and configuring the infrastructure.

### Signup for Reddit and Create Reddit API

In this project, the [Reddit API](https://www.reddit.com/dev/api/) is used to extract data from Reddit. Follow the step for initial setup

1. Creat [Reddit Account](https://www.reddit.com/)

2. Login into the Reddit account and go to https://www.reddit.com/prefs/apps to create an app.

3. Click the button 'Create an App' at the bottom and fill in the required informatiom

   * _Name_: Choose a name for your app
   * _Select_: Select **script** from the given options
   * _description_: optional 
   * _redirect uri_: Use http://localhost:8080 as a redirect URI

4. Click 'create app' and note down **Client ID** and **Client Secret** keys

5. On the VM instance, create an _.env_ file in the project folder _/WEEK_7_PROJECT_ and define following variables 

   * _secret_id_ = Use Client Secret keys generated by reddit app
   * _client_id_ = Use Client ID keys from generated by reddit app

### Create Infrastructure with Terraform

1. Make sure the VM is running (check in Google Console) and ssh into the VM

```
ssh dtc-dtc-de-zoomcap-project-vm
```

2. Go to the `terraform` folder


3. Set environment variable to point to the location of the transferred .json file 

```
export GOOGLE_APPLICATION_CREDENTIALS=~/.keys/constant-haven-384713-7ff3313
```

6. Use the Service-Account credentials for authentification

```
gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
```

4. Initialize Terraform

```
terraform init
```

5. Plan infrastructure

```
terraform plan -var="project=<your-gcp-project-id>"
```

6. Create new infrastructure (or apply changes)

```
terraform apply -var="project=<your-gcp-project-id>"
```

### Initialize and Setup Prefect

This section describes how the entire workflow, extracting, transforming and uploading to data GCS/BQ gets orchestrated with Prefect.

The `flows` folder contains two files which takes care of the entire workflow orchestatrion with **Prefect**. 

1. `elt_web_to_gcs.py` 

This script extracts data from the popular subreddit Wallstreetbets, cleans and transforms it, and then uploads the resulting files to Google Cloud Storage (GCS). The script uses the Extract-Load-Transform (ELT) approach to process the data, which involves extracting raw data from the source, loading it into a data processing environment, and then transforming it to a usable format. In this case, the script extracts posts from Wallstreetbets along with attributes such as author, number of comments etc. using the Reddit API, cleans and transform the data, and then saves the Data as .csv files before uploading to GCS.

> Note: The following parameters are used in these project (check in file `extract_reddit_data_etl.py`) but can be changed at anytime. 

    * **subreddit_name** = "WallStreetBets"
    * **time_filter** = "day"
    * **post_limit** = 10

2. `etl_gcs_to_bq.py`

This script extracts the data from Google Cloud Storage applies further transformations to the data such as data cleansing, aggregation, and data type conversions. Finally, the transformed data is uploaded to BQ in a specified table.

To proceed further, every step in [gettingstarted](data-engineering-zoomcamp/week_7_project/README.md) must be completed, so that the next step of executing and deploying the workflow doesn't rise any unexpected issues.  

Next step, configure Prefect to interact with GCP services within Prefect flows.

1. Start Prefect UI from terminal 
```
prefect orion start
```
2. Go to the Prefect UI and select *+Block** from the menu

![Select Block from Prefect UI](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Select_Block_from_Prefect_UI.png?raw=true)

3. Click **Add Block** and search for **GCS Bucket**

![Add Block in Prefect UI](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Add_Block_in_Prefect_UI.png?raw=true)

![Select GCS Bucket Block in Prefect UI](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Select_GCS_Bucket_Block_in_Prefect_UI.png?raw=true)

4. Fill in the *+Block Name** and name of the *+Bucket** which was set when creating the infrastructure with terraform 

![Create GCS Bucket Block in Prefect UI](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Create_GCS_Bucket_Block_in_Prefect_UI.png?raw=true)

5. Click on **GCP Credentials** to create another Block and add the content of the .json file which was created when setting up the Service Account 

![Create GCS Cred Block in Prefect UI](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Create_GCS_Cred_Block_in_Prefect_UI.png?raw=true)

![Add Service Account .json file in Prefect UI](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Add_Service_Account_.json_file_in_Prefect_UI.png?raw=true)

6. Select the newly created **GCP Cred** Block

![Select GCP Cred Block in Prefect UI](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Select_GCP_Cred_Block_in_Prefect_UI.png?raw=true)

7. Now, the code snippet generated can be passed into the flow codes to use the Blocks 

![Copy Code Snippet for GCS Bucket Block from Prefect UI into Flow Codes](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Copy_Code_Snippet for_GCS_Bucket_Block_from_Prefect_UI_into_Flow_Codes.png?raw=true)

### Deploy Workflow with Prefect

1. Activate virtuel enviroment

```
conda activate dezoomcamp
```

2. From the home directory, move to the `/flows` directory

```
cd /data-engineering-zoomcamp/week_7_project/flows
```

3. Run following commands to deploy the workflow with a specifc schedule (defined by **--cron "0 0 * * *"**)

```
prefect deployment build etl_web_to_gcs.py:etl_web_to_gcs -n 'Reddit ETL' --cron "0 0 * * *" -a
```  

In the Prefect UI under Deployments the newly created flow can be seen

![Workflow Deployment with Prefect](https://github.com/[zenofanalytics]/[week_7_project]/blob/[main]/[assets]Workflow_Deployment_with_Prefect.png?raw=true)

>`After running the code, another filed .yaml will be created which basically contains all the metadata that the Prefect needs to know in order to start orchestrating`

4. Start an agent that puls work from the an work queue:
```  
prefect agent start  --work-queue "default"
```  
### Visualize with Looker Studio 

Use Looker Studio to create visualizations based on the data stored in BQ table.

1. Go to Looker Studio and sign in

2. Choose New -> Data Source

3. Select BigQuery connector

4. Select `Project-ID > Dataset > Table` 

5. Click `CONNECT > CREATE REPORT`

### Stop Everything from Running

To destroy all remote objects and remove the stack from the cloud, run the following command from the terminal 

```
terraform destroy
```

## Roadmap 

* Add tests
* Add CI/CD tooling to automate the workflow and make it more production ready
* Add docker containers to aid with reproducibility of the presented ETL pipeline
* Implement dbt for transforming and preparing data on DWH
* Enrich data with other resources such as other subreddits, tweets, news about specific stocks, stock market data etc. to add more functionalities and extend the scope of the NLP analysis
* Improve project documentation


## Acknowledgements

Thank you DataTalks.Club for creating this course! And a big Thank You to [Alexey Grigorev](https://github.com/alexeygrigorev) for beeing such a great teacher! 