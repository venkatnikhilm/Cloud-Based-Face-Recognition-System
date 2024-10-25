# Cloud-Based Face Recognition System

This project implements an **elastic, cloud-based face recognition system** using AWS resources, including S3, SQS, and EC2 instances with autoscaling. It is designed to process image uploads through a multi-tiered architecture, scaling dynamically based on incoming request volume.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Components](#key-components)
- [Setup and Deployment](#setup-and-deployment)
- [Usage](#usage)
- [Workload Generator](#workload-generator)
- [Systemd Services](#systemd-services)

## Overview

The system receives images for face recognition via a web interface, which are uploaded to an S3 bucket. These images are processed by the **App Tier** for face recognition, with results stored in another S3 bucket and sent to an SQS response queue. The App Tier autoscaling is controlled by a custom autoscaler that adjusts the number of EC2 instances based on queue length.

## Architecture

The project is designed in three main tiers:

1. **Web Tier** - A Node.js server for receiving image files via a POST request, which are uploaded to an S3 bucket and added to an SQS request queue.
2. **App Tier** - Python EC2 instances that poll the SQS queue, process images using a face recognition model, and save results to an S3 output bucket.
3. **Autoscaling Controller** - A controller script that adjusts the number of App Tier instances based on the SQS request queue length, ensuring efficient resource allocation.

## Key Components

- **AWS S3** - Used for storing incoming images and recognition results.
- **AWS SQS** - Used as the message broker between the Web Tier and App Tier.
- **AWS EC2** - Hosts the Web Tier and App Tier. The App Tier dynamically scales based on workload.
- **Node.js and Express** - Handles HTTP requests in the Web Tier.
- **Python (face recognition)** - Processes images in the App Tier using [facenet-pytorch](https://github.com/timesler/facenet-pytorch).

## Setup and Deployment

### Prerequisites

- AWS CLI, configured with access to S3, SQS, and EC2.
- Node.js (v14+) and Python 3.7+
- Python libraries in `requirements.txt` (for App Tier).
- npm libraries in `package.json` (for Web Tier).

### Deployment Steps

1. **Set up AWS resources:**
   - Create S3 buckets for input and output.
   - Create SQS queues for requests and responses.

2. **Configure EC2 instances:**
   - Create a base App Tier EC2 instance with `script.py` to process images, and create an AMI from this instance.
   - Launch the Web Tier instance with `index.js`.

3. **Configure Autoscaler:**
   - Deploy `controller.py` with a systemd service to monitor and scale App Tier instances based on SQS queue length.

4. **Start the System:**
   - Run the Web Tier and start the workload generator to test the scaling and processing.

### Environment Variables

Configure the following environment variables in `.env` for Web Tier:
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `PORT`

## Usage

To start the Web Tier server:

```bash
node index.js
```
### To send requests using the workload generator:

```bash
python3 workload_generator.py --num_request <number> --url 'http://<web-tier-ip>:3001/' --image_folder "<path-to-images>"
```
