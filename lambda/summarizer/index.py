import json
import boto3
from botocore.config import Config
from youtube_transcript_api import YouTubeTranscriptApi
import logging
import html

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_video_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        logger.error(f"An error occurred while fetching transcript: {e}")
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
    
    prompt = f"""Summarize the following YouTube video transcript into one or more clear and 
    readable paragraphs. Capture the main ideas discussed, any key topics you identify, 
    and any other interesting parts of the content. At the end of your summary, 
    give a bullet point list of the key takeaways and any action items if applicable:

    {text}
    """

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                }
            ]
        }
    ]

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "system": "You are an AI assistant that excels at summarizing YouTube video transcripts.",
            "messages": messages,
            "temperature": 1.0,
            "top_p": 0.999,
            "top_k": 40
        }
    )

    try:
        logger.info("Invoking Bedrock model")
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0", 
            body=body
        )
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    except Exception as e:
        logger.error(f"An error occurred while summarizing text: {e}")
        return None

def format_summary(summary):
    # Split the summary into paragraphs
    paragraphs = summary.split('\n\n')
    
    # Format each paragraph
    formatted_paragraphs = [f'<p>{html.escape(p.strip())}</p>' for p in paragraphs if p.strip()]
    
    # Check if the last paragraph contains bullet points
    if '•' in paragraphs[-1] or '-' in paragraphs[-1]:
        # Split the last paragraph into bullet points
        bullet_points = paragraphs[-1].split('\n')
        formatted_bullets = '<ul>'
        for point in bullet_points:
            if point.strip().startswith('•') or point.strip().startswith('-'):
                formatted_bullets += f'<li>{html.escape(point.strip()[1:].strip())}</li>'
        formatted_bullets += '</ul>'
        # Replace the last paragraph with formatted bullet points
        formatted_paragraphs[-1] = formatted_bullets
    
    # Join all formatted parts
    formatted_summary = ''.join(formatted_paragraphs)
    
    # Wrap the entire summary in a div with some basic styling
    styled_summary = f'''
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2c3e50;">Video Summary</h2>
        {formatted_summary}
    </div>
    '''
    
    return styled_summary

def handler(event, context):
    try:
        body = json.loads(event['body'])
        video_url = body['youtube_url']
        video_id = video_url.split('v=')[1]
        
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
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'summary': summary
            })
        }
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'An unexpected error occurred: {str(e)}')
        }
