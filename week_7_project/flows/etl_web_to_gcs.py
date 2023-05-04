# Import necessary modules
import os
from pathlib import Path
import csv
from decouple import config

#Config files
import pandas as pd
import datetime as dt


#Reddit API wrapper
import praw

#Workflow orchestration
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket

#Sentiment analysis
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, RegexpTokenizer 
from nltk.corpus import stopwords
import spacy


# Config Variables
SECRET_ID = config("secret_id")
CLIENT_ID = config("client_id")


@task(log_prints=True)
def extract(top_posts_list):
    """"Extract reddit data into pandasDataFrame"""

    # Create an empty DataFrame to store the data
    df = pd.DataFrame(columns=['title', 'author','score','upvote_ratio','created_utc','url'])

    # Loop over the top posts and append the data to the DataFrame
    for post in top_posts_list:
        df = df.append({
            'title': post.title, 
            'author': post.author, 
            'created_utc': post.created_utc, 
            'score': post.score, 
            'num_comments': post.num_comments,
            'total_awards_received': post.total_awards_received,
            'upvote_ratio': post.upvote_ratio, 
            'url': post.url}, ignore_index=True)

    print(df)

    return df


def transform(df_top_posts):
    """Fix dtype issues"""
    
    df_top_posts['created_utc'] = pd.to_datetime(df_top_posts['created_utc'], unit='s')

    print(len(df_top_posts))
    print(df_top_posts.dtypes)
    
    # Initialize the sentiment analyzer
    nltk.download('vader_lexicon')
    sia = SentimentIntensityAnalyzer()

    # Apply sentiment analysis to each title in the dataframe
    df_top_posts['positive_sentiment'] = df_top_posts['title'].apply(lambda x: sia.polarity_scores(x)['pos'])
    df_top_posts['negative_sentiment'] = df_top_posts['title'].apply(lambda x: sia.polarity_scores(x)['neg'])
    df_top_posts['neutral_sentiment'] = df_top_posts['title'].apply(lambda x: sia.polarity_scores(x)['neu'])
    df_top_posts['compound_sentiment'] = df_top_posts['title'].apply(lambda x: sia.polarity_scores(x)['compound'])
    
    
    # add sentiment column based on compound_sentiment threshold
    threshold = 0.3
    df_top_posts['sentiment'] = ['positive' if x >= threshold else 'negative' if x <= -threshold else 'neutral' for x in df_top_posts['compound_sentiment']]
    
    
    #Identify Ticker or Company Names
    nlp = spacy.load("en_core_web_sm")
    
    excluded_names = ["SEC", "Fed", "the Federal Reserve", "ECB", "CNBC", "FDA", "Fidelity", "Reddit","Robinhood", "FOMC"]
    df_top_posts['org'] = df_top_posts['title'].apply(lambda x: ', '.join([ent.text for ent in nlp(x).ents if ent.label_ == 'ORG' and ent.text not in excluded_names]) or 'No ticker found')
    
    return df_top_posts

@task()
def save_to_local(df_transformed, filename):
    """Write DataFrame out locally as csv file"""

    # Get the current date
    date_today = dt.date.today().strftime('%Y-%m-%d')

    # Create a new filename with the current date
    filename = filename.replace('.csv', f'_{date_today}.csv')

    # Create the data directory if it does not exist
    project_Dir = "data-engineering-zoomcamp/week_7_project" # Please Change file path if needed
    path = Path(f'data/{filename}')
    path.parent.mkdir(parents=True, exist_ok=True)
    print(path)

    # Save the DataFrame to a csv file
    df_transformed.to_csv(path, index=False)
    
    return path

@task()
def write_gcs(path):
    """Upload local .csv files to GCS"""
    gcs_block = GcsBucket.load("dezoomcamp-gcs")
    gcs_block.upload_from_path(
        
        from_path = path , to_path=path
    )

    return

@task(log_prints=True, retries=3)
def get_top_posts(subreddit_name, time_filter, post_limit):
    """Connect to the subreddit and retrieve the top posts"""

    # Initialize the Reddit instance with your API credentials
    reddit = praw.Reddit(client_id= CLIENT_ID,
                         client_secret=SECRET_ID,
                         user_agent='ZenOfAnalytics')

    # Connect to the subreddit and retrieve the top posts
    subreddit = reddit.subreddit(subreddit_name)
    top_posts = subreddit.top(time_filter=time_filter, limit=post_limit)

    top_posts_list = list(top_posts)

    return top_posts_list


@flow(log_prints=True)
def etl_web_to_gcs():
    """"Main ETL flow to extract data and load into GCS"""

    subreddit_name = "WallStreetBets"
    time_filter = "day"
    post_limit = 10
    
    top_posts_list = get_top_posts(subreddit_name, time_filter, post_limit)
    
    df_top_posts = extract(top_posts_list)
    
    df_transformed = transform(df_top_posts)
    print(df_transformed.info())
    
    filename = f"reddit_{subreddit_name}.csv"
    path = save_to_local(df_transformed, filename)

    write_gcs(path)

if __name__ == '__main__':
    etl_web_to_gcs()
