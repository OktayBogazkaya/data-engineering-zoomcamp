from confluent_kafka import Producer, Consumer, KafkaError
import csv
from time import sleep
from collections import Counter


def read_ccloud_config(config_file):
    conf = {}
    with open(config_file) as fh:
        for line in fh:
            line = line.strip()
            if len(line) != 0 and line[0] != "#":
                parameter, value = line.strip().split('=', 1)
                conf[parameter] = value.strip()
    return conf

# Topic to produce and consum messages to/from
topic = 'pu_locationid_popularity'

# Kafka producer configuration
producer = Producer(read_ccloud_config("client.properties"))

# Create dictionary to count unique PULocationID's
location_list = []

# Load green tripdata from CSV file and add PULocationIDs to location_list
with open('green_tripdata_2019-01.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        message = row['PULocationID']
        location_list.append(message)

# Load fhv tripdata from CSV file and add PULocationIDs to location_list
with open('fhv_tripdata_2019-01.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        message = row['PUlocationID']
        location_list.append(message)

# Get the count of each PULocationID and produce the top 5 to Kafka
location_count = Counter(location_list)
for location_id, count in location_count.most_common(5):
    message = location_id
    producer.produce(topic, message.encode('utf-8'))

# Flush producer messages to Kafka
producer.flush()

# Wait for a few seconds to ensure all messages have been produced before the consumer starts polling
sleep(5)

# Kafka consumer configuration
props = read_ccloud_config("client.properties")
props["group.id"] = "consumer-group-pu-location-popularity-1"
props["auto.offset.reset"] = "earliest"

consumer = Consumer(props)
consumer.subscribe([topic])

# Consume messages from Kafka
msg = consumer.poll(1.0)

if msg is None:
    print("No messages received")
else:
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
    else:
        # Append the PULocationID to the location_list
        location_list.append(msg.value().decode('utf-8'))

        # Get the count of each PULocationID and print the top 5 most popular ones
        location_count = Counter(location_list)
        for location_id, count in location_count.most_common(5):
            print("PULocationID {} has count {}".format(location_id, count))