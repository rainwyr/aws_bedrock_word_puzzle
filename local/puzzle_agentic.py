import boto3
import uuid

BUCKET_NAME = "word-puzzle-421"
SOLUTIONS_FOLDER = "solutions/"

AGENT_ID = "02WMEXEHEB"
AGENT_ALIAS_ID = "GYLK8I0PAJ"

bedrock_agent = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='us-east-1'
)

session_id = str(uuid.uuid4())

response = bedrock_agent.invoke_agent(
    agentId=AGENT_ID,
    agentAliasId=AGENT_ALIAS_ID,
    sessionId=session_id,
    inputText="Can you generate and store a puzzle for 'Festival'?"
)

event_stream = response.get("completion")

for event in event_stream:
    decoded_text = event["chunk"]["bytes"].decode("utf-8")
    print(decoded_text)
