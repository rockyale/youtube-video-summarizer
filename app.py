#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from lib.youtube_summarizer_stack import YoutubeSummarizerStack

app = App()
YoutubeSummarizerStack(app, "YoutubeSummarizerStack",
    env=Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
)

app.synth()