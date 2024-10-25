const S3 = require("aws-sdk/clients/s3");
const fs = require("fs");

const bucketName = "1228911985-in-bucket";  // Use your input S3 bucket
const region = "us-east-1";

const s3 = new S3({
  region,
});

function uploadImageToS3(file) {
  const fileStream = fs.createReadStream(file.path);

  const uploadParams = {
    Bucket: bucketName,
    Body: fileStream,
    Key: file.originalname,
  };

  return s3.upload(uploadParams).promise();
}

module.exports = {
  uploadImageToS3,
};