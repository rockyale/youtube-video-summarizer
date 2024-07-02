import json
import os
import boto3

def handler(event, context):
    if event['httpMethod'] == 'GET':
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>YouTube Video Summarizer</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                #summarizer-form {
                    margin-bottom: 20px;
                }
                #youtube-url {
                    width: 70%;
                    padding: 10px;
                    margin-right: 10px;
                }
                button {
                    padding: 10px 20px;
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
                button:hover {
                    background-color: #45a049;
                }
                #summary {
                    background-color: #f9f9f9;
                    border: 1px solid #ddd;
                    padding: 20px;
                    margin-top: 20px;
                }
                #summary h2 {
                    color: #2c3e50;
                    margin-top: 0;
                }
                #summary ul {
                    padding-left: 20px;
                }
                .disclaimer {
                    font-size: 0.8em;
                    color: #666;
                    margin-top: 10px;
                    padding: 10px;
                    background-color: #f0f0f0;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <h1>YouTube Video Summarizer</h1>
            <div class="disclaimer">
                <strong>Disclaimer:</strong> This is a serverless summarizer web app. It utilizes the unofficial YouTube Transcript API, which depends on the availability of transcripts or automatically generated subtitles for videos. If these are not available, summarization will not occur. The summarization process is carried out using Claude Sonnet 3.0.
            </div>
            <form id="summarizer-form">
                <input type="text" id="youtube-url" placeholder="Enter YouTube URL" required>
                <button type="submit">Summarize</button>
            </form>
            <div id="summary"></div>

            <script>
                function formatSummary(summary) {
                    const paragraphs = summary.split('\\n\\n');
                    let formattedSummary = '<h2>Video Summary</h2>';
                    
                    paragraphs.forEach((paragraph, index) => {
                        if (index === paragraphs.length - 1 && (paragraph.includes('•') || paragraph.includes('-'))) {
                            const points = paragraph.split('\\n');
                            formattedSummary += '<h3>' + points[0] + '</h3><ul>';
                            points.slice(1).forEach(point => {
                                formattedSummary += '<li>' + point.replace(/^[•-]\s*/, '') + '</li>';
                            });
                            formattedSummary += '</ul>';
                        } else {
                            formattedSummary += '<p>' + paragraph + '</p>';
                        }
                    });
                    
                    return formattedSummary;
                }

                document.getElementById('summarizer-form').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const youtubeUrl = document.getElementById('youtube-url').value;
                    const summaryDiv = document.getElementById('summary');
                    summaryDiv.innerHTML = 'Summarizing...';

                    try {
                        const response = await fetch(window.location.href, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ youtube_url: youtubeUrl }),
                        });

                        if (response.ok) {
                            const data = await response.json();
                            summaryDiv.innerHTML = formatSummary(data.summary);
                        } else {
                            const errorData = await response.text();
                            summaryDiv.innerHTML = `Error: ${errorData}`;
                        }
                    } catch (error) {
                        summaryDiv.innerHTML = `Error: ${error.message}`;
                    }
                });
            </script>
        </body>
        </html>
        """
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': html_content
        }
    elif event['httpMethod'] == 'POST':
    # Forward the request to the summarizer Lambda
        lambda_client = boto3.client('lambda')
        response = lambda_client.invoke(
            FunctionName=os.environ['SUMMARIZER_FUNCTION_NAME'],
            InvocationType='RequestResponse',
            Payload=event['body']
        )
        
        # Parse the response from the summarizer Lambda
        response_payload = json.loads(response['Payload'].read())
        
        # Return the JSON content
        return {
            'statusCode': response_payload['statusCode'],
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': response_payload['body']
        }