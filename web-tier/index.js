require("dotenv").config();
const {
    sendMessageToSqs,
    receiveMessageFromSqs,
  } = require("./service/sqsMessageService.js");
  const { uploadImageToS3 } = require("./service/s3UploadService.js");
const util = require("util");
const multer = require("multer");
const fs = require("fs");
const express = require("express");
const unlinkFile = util.promisify(fs.unlink);

const PORT = process.env.PORT || 3001;

const app = express();
app.use(express.json());
const upload = multer({ dest: __dirname + "/uploads/" });

app.post("/", upload.single("inputFile"), async (req, res) => {
  // Upload the image to S3 bucket
  const s3Result = await uploadImageToS3(req.file);
  
  // Clean up local copy of the uploaded file
  await unlinkFile(req.file.path);
  
  if (s3Result) {
    // Send message to SQS with the image name
    const sqsResult = await sendMessageToSqs(req.file.originalname, res);
    
    if (sqsResult != undefined) {
      // Poll the response from the App Tier (from SQS response queue)
      await receiveMessageFromSqs(req.file.originalname, res);
    }
  }
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`Web Tier server running on port ${PORT}`);
});