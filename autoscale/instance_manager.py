import boto3

# Initialize EC2 client
ec2_client = boto3.client('ec2', region_name='us-east-1')

# Configuration for new App Tier instances
AMI_ID = "ami-0303e28d85dcc4afc"  
ROLE_ARN = "arn:aws:iam::509399621571:instance-profile/sqs-s3-ec2-full-access"
KEY_NAME = "venkatnikhilmangipudi" 
TAG_SPEC = [
    {
        "ResourceType": "instance",
        "Tags": [
            {
                "Key": "NAME",
                "Value": "App-Instance"
            }
        ]
    }
]
def create_instance():
    instance_num = len(get_running_instances()) + 1
    TAG_SPEC = [
        {
            "ResourceType": "instance",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": f"app-tier-instance-{instance_num}"  # Naming format for App Tier instances
                }
            ]
        }
    ]
    
    instances = ec2_client.run_instances(
        ImageId=AMI_ID,
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName=KEY_NAME,
        IamInstanceProfile={"Arn": ROLE_ARN},
        TagSpecifications=TAG_SPEC
    )
    
    print(f"Creating instance: {instances['Instances'][0]['InstanceId']}")

def multiple_instance_create(num):
    print("Creating ", num, " instances")
    for _ in range(num):
        create_instance()

def start_instance(instance_id):
    print(f'Starting instance: {instance_id}')
    response = ec2_client.start_instances(InstanceIds=[instance_id])
    print(response)

def stop_instance(instance_id):
    print(f'Stopping instance: {instance_id}')
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)

def get_running_instances():
    instance_list = []
    reservations = ec2_client.describe_instances(Filters=[
        {"Name": "instance-state-name", "Values": ["running", "pending"]}
    ]).get("Reservations")
    
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_list.append(instance_id)
    
    print(f"Running instances: {instance_list}")
    return instance_list

def get_stopped_instances():
    instance_list = []
    reservations = ec2_client.describe_instances(Filters=[
        {"Name": "instance-state-name", "Values": ["stopped"]}
    ]).get("Reservations")
    
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_list.append(instance_id)
    
    print(f"Stopped instances: {instance_list}")
    return instance_list

def get_all_instances():
    instance_list = []
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running", "stopped"],
        }
    ]).get("Reservations")

    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_list.append(instance_id)
    print("All instances: ", instance_list)
    return instance_list

def start_multiple_instances(instance_ids):
    print("Starting instances ", instance_ids)
    for i in instance_ids:
        start_instance(i)

def stop_multiple_instances(instance_ids):
    print("Stopping instances: ", instance_ids)
    for i in instance_ids:
        stop_instance(i)