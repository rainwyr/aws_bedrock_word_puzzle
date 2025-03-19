import boto3
import json
import logging
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")
BUCKET_NAME = "word-puzzle-421"
PUZZLES_FOLDER = "puzzles/"
SOLUTIONS_BY_ID_FOLDER = "solutions_by_id/"
SOLUTIONS_BY_WORD_FOLDER = "solutions_by_word/"

def upload_puzzle_to_s3(target_word, descriptions):
    try:
        puzzle_id = str(uuid.uuid4())  # Generate a unique puzzle ID

        # Create the puzzle file (without target word)
        puzzle_data = {
            "puzzle_id": puzzle_id,
            "descriptions": descriptions
        }
        puzzle_key = f"{PUZZLES_FOLDER}{puzzle_id}.json"
        s3.put_object(Body=json.dumps(puzzle_data, indent=2).encode("utf-8"), 
                      Bucket=BUCKET_NAME, Key=puzzle_key)

        # Create the solution file (with target word)
        solution_data = {
            "puzzle_id": puzzle_id,
            "target_word": target_word,
            "descriptions": descriptions
        }

        # Save solution by ID
        solution_by_id_key = f"{SOLUTIONS_BY_ID_FOLDER}{puzzle_id}.json"
        s3.put_object(Body=json.dumps(solution_data, indent=2).encode("utf-8"), 
                      Bucket=BUCKET_NAME, Key=solution_by_id_key)

        # Save solution by target word
        solution_by_word_key = f"{SOLUTIONS_BY_WORD_FOLDER}{target_word}.json"
        s3.put_object(Body=json.dumps(solution_data, indent=2).encode("utf-8"), 
                      Bucket=BUCKET_NAME, Key=solution_by_word_key)

        return (f"✅ Puzzle uploaded successfully.\n"
                f"- Puzzle (No answer): {puzzle_key}\n"
                f"- Solution by ID: {solution_by_id_key}\n"
                f"- Solution by Word: {solution_by_word_key}")

    except Exception as e:
        logger.error(f"Error uploading puzzle: {str(e)}")
        return f"❌ Error: {str(e)}"

def retrieve_puzzle_from_s3(identifier, search_by="id"):
    try:
        if search_by == "id":
            key = f"{SOLUTIONS_BY_ID_FOLDER}{identifier}.json"
        elif search_by == "word":
            key = f"{SOLUTIONS_BY_WORD_FOLDER}{identifier}.json"
        else:
            return "❌ Invalid search type. Use 'id' or 'word'."

        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        solution_data = json.loads(response['Body'].read().decode("utf-8"))

        return (f"✅ Successfully retrieved puzzle.\n"
                f"- Puzzle ID: {solution_data['puzzle_id']}\n"
                f"- Target Word: {solution_data['target_word']}\n"
                f"- Descriptions: {solution_data['descriptions']}")

    except s3.exceptions.NoSuchKey:
        return f"❌ No puzzle found for {search_by} '{identifier}'."
    except Exception as e:
        logger.error(f"Error retrieving puzzle: {str(e)}")
        return f"❌ Error: {str(e)}"

def lambda_handler(event, context):
    logger.info(f"Full event: {json.dumps(event, indent=2)}")

    action = event.get('function', '').strip()
    parameters = event.get('parameters', [])
    param_dict = {param["name"]: param["value"] for param in parameters}

    target_word = param_dict.get("target_word", "unknown-word")
    descriptions = param_dict.get("descriptions", [])
    identifier = param_dict.get("identifier", "")
    search_by = param_dict.get("search_by", "id")  # "id" or "word"

    logger.info(f"Action: {action}, Target Word: {target_word}")

    if action == "upload_puzzle_to_s3":
        response_message = upload_puzzle_to_s3(target_word, descriptions)
    elif action == "retrieve_puzzle_from_s3":
        response_message = retrieve_puzzle_from_s3(identifier, search_by)
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
