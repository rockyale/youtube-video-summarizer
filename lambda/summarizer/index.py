import json
import boto3
from botocore.config import Config
from youtube_transcript_api import YouTubeTranscriptApi
import re
import urllib.parse

def extract_video_id(url):
    # Handle full YouTube URLs
    youtube_regex = r'(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)'
    match = re.search(youtube_regex, url)
    if match:
        return match.group(4)
    
    # Handle short YouTube URLs
    short_regex = r'(https?://)?(www\.)?youtu\.be/([-\w]+)'
    match = re.search(short_regex, url)
    if match:
        return match.group(3)
    
    # Handle URLs with additional parameters
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.netloc in ['youtube.com', 'www.youtube.com', 'youtu.be']:
        if parsed_url.path.startswith('/watch'):
            return urllib.parse.parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.netloc == 'youtu.be':
            return parsed_url.path[1:]
    
    return None

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        print(f"An error occurred while fetching transcript: {e}")
        return None

def summarize_text(text):
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1',  # replace with your preferred region
        config=Config(
            retries = {
                'max_attempts': 10,
                'mode': 'standard'
            }
        )
    )
    
    prompt = f"""Human: Summarize the following YouTube video transcript in 500 words or less. 
    Focus on the main topic, key points, and top ideas:

    {text}

    Assistant: Certainly! I'll provide a concise summary of the YouTube video transcript, focusing on the main topic, key points, and top ideas in 500 words or less.

    Human: Great, please proceed with the summary.

    Assistant:"""

    try:
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }),
            contentType="application/json"
        )

        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    except Exception as e:
        print(f"An error occurred while summarizing text: {e}")
        return None

def handler(event, context):
    try:
        body = json.loads(event['body'])
        video_url = body['youtube_url']
        video_id = extract_video_id(video_url)
        
        if not video_id:
            return {
                'statusCode': 400,
                'body': json.dumps('Invalid YouTube URL')
            }
        
        transcript = get_video_transcript(video_id)
        
        if not transcript:
            return {
                'statusCode': 400,
                'body': json.dumps('Failed to retrieve video transcript')
            }
        
        summary = summarize_text(transcript)
        
        if not summary:
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to summarize video')
            }

        return {
            'statusCode': 200,
            'body': json.dumps({
                'summary': summary
            })
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'An unexpected error occurred: {str(e)}')
        }
