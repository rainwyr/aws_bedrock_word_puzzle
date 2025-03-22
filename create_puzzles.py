import uuid
import time
import boto3
from botocore.config import Config


AGENT_ID = "3OR1X5NSQW"
AGENT_ALIAS_ID = "TCOS0RN3A5"

config = Config(
    read_timeout=120,
    connect_timeout=30,
    retries={
        'max_attempts': 2,
        'mode': 'standard'
    }
)

bedrock_agent = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='us-east-1',
    config=config
)

target_words = ["Bark", "Light", "Scale"]
# target_words = ["Spring", "Check", "Bank", "Pitch", "Match", "Board", "Block"]
# target_words = [
#     "Rock", "Ring", "Bat", "Drill", "Break", "Fall", "Seal", "Wave", "Mouse", "Jam", 
#     "Crane", "Point","Train", "Lead", "Watch", "Date", "Stamp", "Trip", "Park", "Fair", 
#     "Toast", "Note", "Bolt", "Iron", "Fly", "Plant", "Star", "Suit", "Fire", "Ball",
#     "Glass", "Line", "Mine", "Root", "Sail", "Score", "Set", "Tie", "Well", "Shot"
# ]

for original_word in target_words:
    target_word = original_word.lower()
    session_id = str(uuid.uuid4())
    input_prompt = f"Create a puzzle for {target_word}"

    print(f"\n🧩 Generating puzzle for: {target_word}")
    try:
        response = bedrock_agent.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=input_prompt
        )

        event_stream = response.get("completion")
        for event in event_stream:
            decoded_text = event["chunk"]["bytes"].decode("utf-8")
            print(decoded_text, end="")

        # Optional: Add a slight pause between requests to avoid throttling
        time.sleep(1)

    except Exception as e:
        print(f"❌ Error generating puzzle for {target_word}: {str(e)}")
