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
