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
        # Get all available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to get the manually created transcript (usually in the original language)
        try:
            transcript = transcript_list.find_manually_created_transcript([])
        except:
            # If no manually created transcript is available, get the first available transcript
            transcript = next(iter(transcript_list))
        
        # Fetch the actual transcript data
        transcript_data = transcript.fetch()
        
        # Join the transcript text
        return ' '.join([entry['text'] for entry in transcript_data])
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
    
    prompt = f"""Human: You are provided with the transcript of a YouTube video. Your task is to generate a detailed summary that adapts in length based on the amount of useful information in the transcript. The summary should highlight the key ideas and elaborate on the main points discussed in each segment of the video. Conclude the summary with either key takeaways or important call-outs. Follow the structure below:

    1. Introduction:

    Begin with a brief introduction that mentions the title of the video, the main topic, and the speaker(s) involved.

    2. Main Content:

    Segmented Summary:

    Divide the content into key segments or episodes based on the natural flow of the conversation.
    For each segment, identify and elaborate on the main ideas discussed.
    Provide detailed explanations for each key point, ensuring to cover all important aspects mentioned by the speaker(s).
    Detail Management:

    If a segment contains a lot of information, ensure that the summary is detailed and covers all critical points.
    If a segment contains less useful information, provide a concise summary focusing on the core ideas.
    3. Conclusion:

    Key Takeaways:

    Summarize the most important points covered in the video.
    Highlight any actionable insights or advice given by the speaker(s).
    Call-Outs:

    If applicable, mention any noteworthy comments, quotes, or suggestions made during the video.
    Include any important resources or references mentioned by the speaker(s).

    {text}

    Assistant: Certainly! I'll provide a summary of the YouTube video transcript, focusing on described instructions

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
