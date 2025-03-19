import boto3
import json
import uuid

s3 = boto3.client("s3")
bedrock_agent_runtime = boto3.client("bedrock-agent-runtime", region_name="us-east-1")

BUCKET_NAME = "word-puzzle-421"
SOLUTIONS_FOLDER = "solutions/"

AGENT_ID = "P1JQEBSVWR"
AGENT_ALIAS_ID = "WGCBW2MI36"
SESSION_ID = str(uuid.uuid4())

def generate_descriptions_from_agent(target_word):
    """
    Calls the Bedrock Agent to generate 4 descriptions that hint at the target word.
    """
    prompt = f"""Generate 4 descriptions that hint at a word but do not explicitly state it.
    The descriptions should each be unique, creative, and engaging.

    Example:
    Target word: "Sun"
    Descriptions:
    1. A brilliant sphere that lights up the sky, warming everything it touches.
    2. The celestial body that marks the start of a new day.
    3. A glowing orb, disappearing beyond the horizon in shades of orange and pink.
    4. The life-giving center of our solar system, essential for all growth.

    Now, generate 4 descriptions for the target word: {target_word}.
    """

    response = bedrock_agent_runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=SESSION_ID,
        inputText=prompt
    )

    full_response_text = ""
    for event in response["completion"]:
        if isinstance(event, dict) and "chunk" in event:
            chunk_data = event["chunk"]
            if isinstance(chunk_data, dict) and "bytes" in chunk_data:
                chunk_text = chunk_data["bytes"].decode("utf-8")
                full_response_text += chunk_text

    descriptions = [desc.strip() for desc in full_response_text.split("\n") if desc.strip()]
    return descriptions[:4]  # Ensure exactly 4 descriptions

def upload_solution_to_s3(target_word, descriptions):
    """
    Uploads the target word and its descriptions as a single JSON file to S3.
    """
    solution_data = {
        "target_word": target_word,
        "descriptions": descriptions
    }
    solution_key = f"{SOLUTIONS_FOLDER}{target_word}_solution.json"

    s3.put_object(Body=json.dumps(solution_data, indent=2).encode("utf-8"), 
                  Bucket=BUCKET_NAME, Key=solution_key)
    print(f"✅ Uploaded solution for '{target_word}' to {solution_key}")

def get_solution_from_s3(target_word):
    """
    Retrieves the solution file from S3.
    """
    solution_key = f"{SOLUTIONS_FOLDER}{target_word}_solution.json"

    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=solution_key)
        solution_data = json.loads(response['Body'].read().decode("utf-8"))
        return solution_data
    except Exception as e:
        print(f"❌ Error retrieving solution from S3: {e}")
        return None

def get_relevance_score_from_agent(target_word, descriptions):
    """
    Calls the Bedrock Agent to evaluate how likely the target_word is the common theme
    among the 4 descriptions on a scale from 0.0 to 1.0.
    """
    descriptions_text = "\n".join(f"{i+1}. {desc}" for i, desc in enumerate(descriptions))

    prompt = f"""Given the 4 descriptions below, determine how likely the word '{target_word}' 
    is the common theme among them. Provide a relevance score between 0.0 and 1.0, rounded 
    to one decimal place (e.g., 0.1 means unlikely, 0.9 means very likely). 

    Descriptions:
    {descriptions_text}

    Respond with only the score as a single float value.
    """

    response = bedrock_agent_runtime.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=SESSION_ID,
        inputText=prompt
    )

    full_response_text = ""
    for event in response["completion"]:
        if isinstance(event, dict) and "chunk" in event:
            chunk_data = event["chunk"]
            if isinstance(chunk_data, dict) and "bytes" in chunk_data:
                chunk_text = chunk_data["bytes"].decode("utf-8")
                full_response_text += chunk_text

    try:
        score = float(full_response_text.strip())
        return round(score, 1)
    except ValueError:
        print(f"❌ Invalid response from agent: {full_response_text}")
        return None

def process_target_word(target_word):
    """
    Generates descriptions, uploads the solution, and prints success message.
    """
    descriptions = generate_descriptions_from_agent(target_word)

    if not descriptions:
        print(f"❌ No descriptions generated for '{target_word}'. Exiting.")
        return

    upload_solution_to_s3(target_word, descriptions)

def evaluate_target_word(target_word):
    """
    Retrieves descriptions from the solution file in S3, asks the agent for a relevance score, and prints results.
    """
    solution_data = get_solution_from_s3(target_word)
    if not solution_data or "descriptions" not in solution_data:
        print("❌ No valid descriptions found in solution. Exiting.")
        return

    descriptions = solution_data["descriptions"]
    relevance_score = get_relevance_score_from_agent(target_word, descriptions)

    if relevance_score is not None:
        print("\n✅ Descriptions Used:")
        for desc in descriptions:
            print(f"- {desc}")
        print(f"\n🌟 Relevance Score: {relevance_score}")
    else:
        print("❌ Failed to retrieve a relevance score.")

target_words = ["Tornado", "Lighthouse"]

for word in target_words:
    print(word)
    process_target_word(word)

for word in target_words:
    print(word)
    evaluate_target_word(word)
