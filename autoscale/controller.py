import instance_manager as ec2_util
import boto3

# Initialize SQS client
sqs_client = boto3.client('sqs', region_name="us-east-1")

# AWS account and SQS queue details
aws_account_id = "509399621571" 
WEB_TIER = "i-0533f73fe40396a33"
sqs_input_queue = f"https://sqs.us-east-1.amazonaws.com/{aws_account_id}/1228911985-req-queue"  # Request queue
sqs_output_queue = f"https://sqs.us-east-1.amazonaws.com/{aws_account_id}/1228911985-resp-queue"  # Response queue

 

# Autoscaling logic
def auto_scale_instances():
    # Get the number of messages in the request queue
    queue_length = int(
        sqs_client.get_queue_attributes(QueueUrl=sqs_input_queue, AttributeNames=['ApproximateNumberOfMessages'])
        .get("Attributes")
        .get("ApproximateNumberOfMessages")
    )
    
    print("Request queue length:", queue_length)

    running_instances = ec2_util.get_running_instances()
    stopped_instances = ec2_util.get_stopped_instances()

    # Remove the Web Tier instance from the scaling logic
    if WEB_TIER in running_instances:
        running_instances.remove(WEB_TIER)

    # If no requests in the queue, scale down App Tier to zero
    if queue_length == 0:
        print("Queue is empty, shutting down all instances except the Web Tier.")
        ec2_util.stop_multiple_instances(running_instances)
        return

    #ensure at least 1 App Tier instance is running
    elif 1 <= queue_length <= 5:
        if len(running_instances) == 0:
            if len(stopped_instances) >= 1:
                ec2_util.start_instance(stopped_instances[0])
            else:
                ec2_util.create_instance()

    #  scale to 10 instances
    elif 5 < queue_length <= 50:
        if len(running_instances) < 10:
            needed_instances = 10 - len(running_instances)
            if len(stopped_instances) >= needed_instances:
                ec2_util.start_multiple_instances(stopped_instances[:needed_instances])
            else:
                ec2_util.start_multiple_instances(stopped_instances)
                for _ in range(needed_instances - len(stopped_instances)):
                    ec2_util.create_instance()

    # scale up to the maximum of 20 instances
    else:
        if len(running_instances) < 20:
            needed_instances = 20 - len(running_instances)
            if len(stopped_instances) >= needed_instances:
                ec2_util.start_multiple_instances(stopped_instances[:needed_instances])
            else:
                ec2_util.start_multiple_instances(stopped_instances)
                for _ in range(needed_instances - len(stopped_instances)):
                    ec2_util.create_instance()

print("Starting Auto Scaling")
auto_scale_instances()