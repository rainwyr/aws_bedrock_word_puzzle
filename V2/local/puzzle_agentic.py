import boto3
import uuid

# BUCKET_NAME = "word-puzzle-421"
# SOLUTIONS_FOLDER = "solutions/"

AGENT_ID = "02WMEXEHEB"
AGENT_ALIAS_ID = "VEQNVC7LAA"

bedrock_agent = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='us-east-1'
)

session_id = str(uuid.uuid4())

response = bedrock_agent.invoke_agent(
    agentId=AGENT_ID,
    agentAliasId=AGENT_ALIAS_ID,
    sessionId=session_id,
    inputText="Find the puzzle_id for 'Spring', use the puzzle_id to retrieve images for Spring"
)

event_stream = response.get("completion")

for event in event_stream:
    decoded_text = event["chunk"]["bytes"].decode("utf-8")
    print(decoded_text)

# Initialize S3 client
s3 = boto3.client('s3')

# Define parameters
bucket_name = "word-puzzle-421"
s3_key = "images/0d014dba-7481-47f2-9640-a2c67a757591_1.png"
local_file_name = "Sprint_1.png"

# Download the file
s3.download_file(bucket_name, s3_key, local_file_name)
print(f"File downloaded successfully as {local_file_name}")