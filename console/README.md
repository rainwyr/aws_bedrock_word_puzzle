# S3
* S3_BUCKET_NAME = "word-puzzle-421"
* SOLUTIONS_FOLDER = "solutions/"

# Lambda Function
```
import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
BUCKET_NAME = "word-puzzle-421"
SOLUTIONS_FOLDER = "solutions/"

def upload_puzzle_to_s3(target_word, descriptions):
    try:
        solution_data = {
            "target_word": target_word,
            "descriptions": descriptions
        }
        solution_key = f"{SOLUTIONS_FOLDER}{target_word}_solution.json"

        s3.put_object(Body=json.dumps(solution_data, indent=2).encode("utf-8"), 
                      Bucket=BUCKET_NAME, Key=solution_key)

        return f"✅ Puzzle for '{target_word}' uploaded successfully to {solution_key}."

    except Exception as e:
        logger.error(f"Error uploading puzzle: {str(e)}")
        return f"❌ Error: {str(e)}"

def retrieve_puzzle_from_s3(target_word):
    try:
        solution_key = f"{SOLUTIONS_FOLDER}{target_word}_solution.json"
        response = s3.get_object(Bucket=BUCKET_NAME, Key=solution_key)
        solution_data = json.loads(response['Body'].read().decode("utf-8"))
        descriptions = solution_data.get("descriptions", "No descriptions found.")

        return f"✅ Successfully retrieved puzzle for '{target_word}'. Descriptions: {descriptions}"

    except Exception as e:
        logger.error(f"Error retrieving puzzle: {str(e)}")
        return f"❌ Error: {str(e)}"

def lambda_handler(event, context):
    logger.info(f"Full event: {json.dumps(event, indent=2)}")

    action = event.get('function', '').strip()
    parameters = event.get('parameters', [])
    param_dict = {param["name"]: param["value"] for param in parameters}

    target_word = param_dict.get("target_word", "unknown-word")
    descriptions = param_dict.get("descriptions", "")

    logger.info(f"Action: {action}, Target Word: {target_word}")

    if action == "upload_puzzle_to_s3":
        response_message = upload_puzzle_to_s3(target_word, descriptions)
    elif action == "retrieve_puzzle_from_s3":
        response_message = retrieve_puzzle_from_s3(target_word)
    else:
        response_message = "❌ Invalid action specified."

    response_body = {
        'TEXT': {
            'body': response_message
        }
    }

    function_response = {
        'actionGroup': event.get("actionGroup", "default-action-group"),
        'function': action,
        'functionResponse': {
            'responseBody': response_body
        }
    }

    session_attributes = event.get('sessionAttributes', {})
    prompt_session_attributes = event.get('promptSessionAttributes', {})

    action_response = {
        'messageVersion': '1.0', 
        'response': function_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }

    return action_response
```

# Bedrock Agent
* Agent name: agent-word-puzzle-421
* Instruction:
```
You are a helpful agent that specializes in creating and evaluating 4-descriptions-1-word puzzles. When asked to create a puzzle, generate 4 descriptions that hint at a word but do not explicitly state it.
    Example: Target word: "Sun"
    Descriptions:
    1. A brilliant sphere that lights up the sky, warming everything it touches.
    2. The celestial body that marks the start of a new day.
    3. A glowing orb, disappearing beyond the horizon in shades of orange and pink.
    4. The life-giving center of our solar system, essential for all growth.
When evaluating a puzzle, given the 4 descriptions and the target_word, determine how likely the target_word is the common theme among them. Provide a relevance score between 0.0 and 1.0, rounded to one decimal place (e.g., 0.1 means unlikely, 0.9 means very likely). 
When interacting with the user, assume "puzzle" means 4-descriptions-1-word puzzles. 
Do not attempt to generate responses yourself. Instead, invoke the function using the provided Lambda function.
```
* Model: Claude 3.5 Sonnet V2
* Action Group: word-puzzle-action-group
  * Use existing Lambda Function `puzzle_manager`
  * Action Function 1: upload_puzzle_to_s3
    * Parameters: target_word, descriptions
  * Action Function 2: retrieve_puzzle_from_s3
    * Parameters: target_word
   
# Chat Example

* What it looks like on Bedrock
  <img width="329" alt="image" src="https://github.com/user-attachments/assets/62245303-7800-4e92-851d-97e788b3c5e4" />
  <img width="330" alt="image" src="https://github.com/user-attachments/assets/68975246-6157-4cc0-aa79-fea213eb68b2" />

* What it looks like on S3 after the chat
  <img width="1427" alt="image" src="https://github.com/user-attachments/assets/a9cc7f19-10b4-4c67-aa32-a634e32b79d1" />


  
