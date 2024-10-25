from fileinput import filename
from botocore.exceptions import ClientError
from urllib import response
import boto3
import json
import os
import subprocess

# Function to get the URL of the SQS queue
def get_queue_url(queue_name):
    sqs_client = boto3.client("sqs", region_name = "us-east-1")
    queue_name = sqs_client.get_queue_url(QueueName = queue_name)
    return queue_name["QueueUrl"]

# Function to write a message to SQS
def write_message(queue_url, message_body):
    sqs_client = boto3.client("sqs", region_name = "us-east-1")
    response = sqs_client.send_message(QueueUrl = queue_url, MessageBody = json.dumps(message_body))
    return response['ResponseMetadata']["HTTPStatusCode"]

# Function to read a message from SQS
def read_message(queue_url):
    sqs_client = boto3.client("sqs", region_name = "us-east-1")
    response = sqs_client.receive_message(QueueUrl = queue_url, MaxNumberOfMessages = 1, WaitTimeSeconds = 10)
    
    if "Messages" in response:
        message_body = json.loads(response["Messages"][0]["Body"])
        receipt_handle = response["Messages"][0]["ReceiptHandle"]
        return message_body["Image_Name"], receipt_handle
    else:
        return None, None

# Function to delete a message from SQS
def delete_message(queue_url, receipt_handle):
    sqs_client = boto3.client("sqs", region_name = "us-east-1")
    sqs_client.delete_message(QueueUrl = queue_url, ReceiptHandle = receipt_handle)

# Function to run the face recognition model
def run_classification_engine(image_path):
    result_filename = '/home/ubuntu/result/' + os.path.splitext(os.path.basename(image_path))[0] + '.txt'
    subprocess.run(['touch', result_filename])
    output_file = open(result_filename, "w")
    subprocess.run(['python3', './face_recognition.py', image_path], stdout=output_file)

# Function to download images from S3
def download_images(s3_bucket_name, image_name):
    s3 = boto3.client("s3")
    file_name = '/home/ubuntu/images/' + image_name
    s3.download_file(s3_bucket_name, image_name, file_name)

# Function to delete local images
def delete_image(image_name):
    file_path = "/home/ubuntu/images/" + image_name
    if os.path.exists(file_path):
        os.remove(file_path)
    else:
        print("File does not exist")

# Function to send classification results to the SQS response queue
def write_classification_msg(image_name, queue_url):
    file_name = os.path.splitext(image_name)[0]
    result_file = '/home/ubuntu/result/' + file_name + '.txt'
    with open(result_file, 'r') as f:
        result = f.readline().strip()
    
    name, confidence = result.split(',')
    sqs_message = {image_name: f"{name}:{confidence}"}  # Include filename:confidence format
    write_message(queue_url, sqs_message)

# Function to upload classification result to S3 (output bucket)
def write_to_bucket(s3_bucket_name, image_name):
    file_name = os.path.splitext(image_name)[0]
    result_file = '/home/ubuntu/result/' + file_name + '.txt'
    with open(result_file, 'r') as f:
        result = f.readline().strip()
    
    name, confidence = result.split(',')
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket = s3_bucket_name, Body = f"{name},{confidence}", Key = file_name)

# Main execution flow
if __name__ == "__main__":
    request_queue = get_queue_url("1228911985-req-queue")
    response_queue = get_queue_url("1228911985-resp-queue")
    input_bucket = "1228911985-in-bucket"
    output_bucket = "1228911985-out-bucket"

    image_name, receipt_handle = read_message(request_queue)
    
    if image_name:
        download_images(input_bucket, image_name)
        run_classification_engine('/home/ubuntu/images/' + image_name)
        write_classification_msg(image_name, response_queue)
        write_to_bucket(output_bucket, image_name)
        delete_message(request_queue, receipt_handle)
        delete_image(image_name)