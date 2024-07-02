from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
    Duration,
)
from constructs import Construct
import subprocess
import os
from build_lambda import build_lambda

class YoutubeSummarizerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create frontend Lambda function
        frontend_lambda = _lambda.Function(
            self, 'FrontendLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='index.handler',
            code=_lambda.Code.from_asset('lambda/frontend'),
            timeout=Duration.seconds(30)
        )

        # Build summarizer Lambda with dependencies
        summarizer_build_path = build_lambda('lambda/summarizer', 'lambda_build')

        # Create summarizer Lambda function
        summarizer_lambda = _lambda.Function(
            self, 'SummarizerLambda',
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler='index.handler',
            code=_lambda.Code.from_asset(summarizer_build_path),
            timeout=Duration.minutes(5)
        )

        # Create API Gateway
        api = apigw.RestApi(
            self, 'YoutubeSummarizerApi',
            rest_api_name='Youtube Summarizer API',
            description='This service summarizes YouTube videos'
        )

        # Add resources and methods to API Gateway
        frontend_integration = apigw.LambdaIntegration(frontend_lambda)
        api.root.add_method('GET', frontend_integration)

        summarizer_integration = apigw.LambdaIntegration(summarizer_lambda)
        api.root.add_method('POST', summarizer_integration)

        # Allow Lambda to invoke Bedrock
        summarizer_lambda.add_to_role_policy(iam.PolicyStatement(
        actions=[
        "bedrock:InvokeModel",
        "bedrock:ListFoundationModels"
         ],
        resources=["*"]
        ))

        # Allow frontend Lambda to invoke summarizer Lambda
        summarizer_lambda.grant_invoke(frontend_lambda)
        frontend_lambda.add_environment('SUMMARIZER_FUNCTION_NAME', summarizer_lambda.function_name)
