const path = require('path');
const AWS = require("aws-sdk");
const bunyan = require("bunyan");

const logger = bunyan.createLogger({
  name: "classificationResponseLogs",
  streams: [
    {
      level: "debug",
      stream: process.stdout,
    },
    {
      level: "info",
      path: "./logs.txt",
    },
  ],
});

// Configure AWS region
AWS.config.update({ region: "us-east-1" });

// Create SQS client
const sqs = new AWS.SQS({ apiVersion: "2012-11-05" });

const awsAccountId = "509399621571";  // Your AWS account ID
const sqsInputQueue = "1228911985-req-queue";  // Your request queue name
const sqsOutputQueue = "1228911985-resp-queue";  // Your response queue name

const sendMessageToSqs = (Image_Name, res) => {
  const params = {
    MessageBody: JSON.stringify({
      Image_Name,
    }),
    QueueUrl: `https://sqs.us-east-1.amazonaws.com/${awsAccountId}/${sqsInputQueue}`,
  };

  return sqs.sendMessage(params, (err, data) => {
    if (err) {
      console.log("Error sending message:", err);
      res.status(400).send({
        message: "Some error occurred",
        data,
      });
    }
  });
};

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

let isFirstReq = true

const receiveMessageFromSqs = async (imageName, res, isFirstReq) => {
  if (isFirstReq) {
    await sleep(65000);  // 30 seconds delay before reading from the response queue
    isFirstReq = false;
  }
    const params = {
        QueueUrl: `https://sqs.us-east-1.amazonaws.com/${awsAccountId}/${sqsOutputQueue}`,
        VisibilityTimeout: 3,
        WaitTimeSeconds: 20,
    };
  sqs.receiveMessage(params, (err, data) => {
    if (err) {
      console.log("Error receiving message:", err);
      res.status(400).send({
        message: "Some error occurred",
        data,
      });
    } else {
      if (data.Messages) {
        const imageData = JSON.parse(data.Messages[0].Body);
        if (Object.keys(imageData)[0] === imageName) {
          const deleteParams = {
            QueueUrl: `https://sqs.us-east-1.amazonaws.com/${awsAccountId}/${sqsOutputQueue}`,
            ReceiptHandle: data.Messages[0].ReceiptHandle,
          };

          sqs.deleteMessage(deleteParams, (err) => {
            if (err) {
              console.log("Error deleting message:", err);
              res.status(400).send({
                message: "Some error occurred",
                data,
              });
            } else {
              const imageNameWithoutExtension = path.parse(imageName).name;
              const classificationResult = imageData[imageName].split(":")[0];
              
    
              res.status(200).send({
                message: `${imageNameWithoutExtension}:${classificationResult}`,
              });
              logger.info(`Served request for image: ${imageNameWithoutExtension}`);
            }
          });
        } else {
          receiveMessageFromSqs(imageName, res);
        }
      } else {
        receiveMessageFromSqs(imageName, res);
      }
    }
  });
};

module.exports = {
  sendMessageToSqs,
  receiveMessageFromSqs,
};