# YouTube Video Summarizer

This is a serverless web application that summarizes YouTube videos using transcripts. It utilizes AWS Lambda, API Gateway, and Claude 3 Sonnet AI model to provide concise summaries of video content.

## Overview

The YouTube Video Summarizer app allows users to input a YouTube video URL and receive a summary of the video's content. It works by:

1. Fetching the video transcript using the YouTube Transcript API (https://pypi.org/project/youtube-transcript-api/)
2. Processing the transcript through Claude 3 Sonnet AI model (although you can change it in Bedrock)
3. Presenting a formatted summary to the user

## Architecture Diagram


![diagram](https://github.com/rockyale/youtube-video-summarizer/assets/133587264/1b082d05-7b4e-4620-ae69-01fa8e67afc9)


## Features

- Serverless architecture using AWS Lambda and API Gateway
- Utilizes the unofficial YouTube Transcript API for fetching video transcripts
- Generates summaries using Claude 3 Sonnet AI model
- Simple and intuitive web interface

## Prerequisites

Before you begin, ensure you have the following:

- An AWS account with appropriate permissions to create and manage Lambda functions, API Gateway, and IAM roles
- Enable access to Sonnet v3, or other model of your choice in your preferred Region in Bedrock console

- Python 3.9 or later installed - (not required for deplyment option 2)  

## Setup and Deployment OPTION 1 - Using local machine

1. Clone this repository:
```
git clone https://github.com/rockyale/youtube-video-summarizer.git
cd youtube-video-summarizer
```

2. Create and activate a virtual environment:
- For Unix or MacOS:
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```
- For Windows:
  ```
  python -m venv venv
  .\venv\Scripts\activate
  ```

3 Install AWS CLI
Download the AWS CLI:
```
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
```
Install the AWS CLI:
```
sudo installer -pkg ./AWSCLIV2.pkg -target /
```

Validate your installation:
```
aws --version
```
Then, configure your AWS account using IAM credentials (or key/secret). Follow the prompts.
```
aws configure
```
4. Install the AWS CDK:
```
npm install -g aws-cdk
```
5. Install the required Python dependencies:
```
pip install -r requirements.txt
```
6. Run the build script to package the Lambda functions with their dependencies:
```
python build_lambda.py
```
7. Bootstrap your AWS environment (if you haven't already):
```
cdk bootstrap
```
8. [OPTIONAL] Update the `lib/youtube_summarizer_stack.py` file with your specific configurations, if necessary. (for example tags, logging options, etc)

9. Deploy the stack:
```
cdk deploy
```
10. Note the API Gateway URL output after deployment. This is the URL you'll use to access your application.

11. To delete stack you can use either
```
 cdk destroy 
```
or manually remove CloudFormation Stack, that will be created by CDK. 

## Setup and Deployment OPTION 2 - Using AWS Cloudshell

You can alternatively use Cloudshell for deployemnt, in this case you do not have to install prerequisites locally. Required packages are already pre-installed for you. 
Run steps 1, 5-10. You can ignore version mismatch messages. cdk destroy does not work due to lack of space, but you can safely remove Cloudformation Stack manually.

## Usage

1. Open the API Gateway URL in a web browser.
2. Enter a YouTube video URL in the input field.
3. Click "Summarize" to generate a summary of the video.
4. The summary will be displayed on the page, including key points and takeaways from the video.

## Project Structure

- `lib/youtube_summarizer_stack.py`: Contains the AWS CDK stack definition
- `lambda/frontend/index.py`: Frontend Lambda function for serving the HTML and handling requests
- `lambda/summarizer/index.py`: Summarizer Lambda function for processing video transcripts and generating summaries
- `app.py`: Entry point for the CDK app

## Limitations

- The app relies on the availability of video transcripts or automatically generated subtitles. If these are not available for a video, summarization will not be possible.
- The quality of the summary depends on the accuracy of the transcript and the performance of the Claude 3 Sonnet AI model.

## Contributing

Contributions to improve the YouTube Video Summarizer are welcome. Please feel free to submit pull requests or create issues for bugs and feature requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This application uses the unofficial YouTube Transcript API and depends on the availability of transcripts or automatically generated subtitles for videos. The summarization process is carried out using Claude 3 Sonnet AI model. This app is for educational and personal use only and is not affiliated with or endorsed by YouTube or Google.

## Acknowledgments

- YouTube Transcript API
- AWS CDK
- Claude 3 Sonnet AI model
