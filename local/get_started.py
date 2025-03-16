import boto3
import uuid
import json

# Find S3
s3 = boto3.client("s3")
BUCKET_NAME = "word-puzzle-421"
SOLUTIONS_FOLDER = "solutions/"
response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=SOLUTIONS_FOLDER)

if "Contents" in response:
    print("Files in S3 descriptions folder:")
    for obj in response["Contents"]:
        print(obj["Key"])
else:
    print("No files found in the descriptions folder.")
print('\n')

# Find Models
bedrock_client = boto3.client("bedrock", region_name="us-east-1")
response = bedrock_client.list_foundation_models()
model_list = response.get('modelSummaries')
print(f"{len(model_list)} models found.")

for model in model_list:
    print(model['modelId'])

bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

response = bedrock_runtime.invoke_model(
    modelId="amazon.titan-text-lite-v1",
    body=json.dumps({
        "inputText": "What is on-demand vs. provision throughput?"
    }),
    accept="application/json",
    contentType="application/json"
)

response_body = json.loads(response['body'].read())
print(response_body["results"][0]["outputText"])
print('\n')

# Find Agents
client = boto3.client("bedrock-agent")
response = client.list_agents()
print(response.get('agentSummaries'))
print('\n')

response = client.list_agent_aliases(agentId="02WMEXEHEB")
print(response.get('agentAliasSummaries'))
print('\n')

bedrock_agent = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='us-east-1'
)

session_id = str(uuid.uuid4())

response = bedrock_agent.invoke_agent(
    agentId='02WMEXEHEB',
    agentAliasId='GYLK8I0PAJ',
    sessionId=session_id,
    inputText="What is on-demand vs. provision throughput?"
)

event_stream = response.get("completion")

for event in event_stream:
    decoded_text = event["chunk"]["bytes"].decode("utf-8")
    print(decoded_text)
