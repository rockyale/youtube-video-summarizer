import aws_cdk as core
import aws_cdk.assertions as assertions
from lib.youtube_summarizer_stack import YoutubeSummarizerStack

def test_lambda_functions_created():
    app = core.App()
    stack = YoutubeSummarizerStack(app, "youtube-summarizer")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "index.handler",
        "Runtime": "python3.9"
    })

def test_api_gateway_created():
    app = core.App()
    stack = YoutubeSummarizerStack(app, "youtube-summarizer")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::ApiGateway::RestApi", 1)

def test_ssm_parameter_created():
    app = core.App()
    stack = YoutubeSummarizerStack(app, "youtube-summarizer")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SSM::Parameter", {
        "Name": "/youtube-summarizer/api-key",
        "Type": "String"
    })
