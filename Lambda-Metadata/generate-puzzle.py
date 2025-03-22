import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
BUCKET_NAME ="word-puzzle-421"

def upload_puzzle_meta_to_s3_from_json(puzzle_json_str):
    try:
        logger.info("Parsing puzzle_json...")
        puzzle = json.loads(puzzle_json_str)

        puzzle_id = puzzle["puzzle_id"]
        target_word = puzzle["target_word"]
        descriptions = puzzle["descriptions"]
        image_urls = puzzle["image_urls"]

        logger.info(f"Uploading puzzle {puzzle_id} with target word '{target_word}'")

        base_puzzle = {
            "descriptions": descriptions,
            "image_urls": image_urls
        }

        puzzle_with_solution = {
            "target_word": target_word,
            **base_puzzle
        }

        # Save to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=f"puzzles/{puzzle_id}.json", Body=json.dumps(base_puzzle), ContentType='application/json')
        s3.put_object(Bucket=BUCKET_NAME, Key=f"solutions_by_id/{puzzle_id}.json", Body=json.dumps(puzzle_with_solution), ContentType='application/json')
        s3.put_object(Bucket=BUCKET_NAME, Key=f"solutions_by_word/{target_word}.json", Body=json.dumps(puzzle_with_solution), ContentType='application/json')

        logger.info(f"Puzzle {puzzle_id} uploaded successfully.")
        return f"✅ Puzzle '{puzzle_id}' saved successfully to S3."

    except Exception as e:
        logger.error(f"❌ Failed to upload puzzle: {e}")
        return f"❌ Error uploading puzzle: {str(e)}"

def lambda_handler(event, context):
    logger.info(f"Full event: {json.dumps(event, indent=2)}")

    action = event.get('function', '').strip()
    parameters = event.get('parameters', [])
    param_dict = {param["name"]: param["value"] for param in parameters}

    puzzle_json_str = param_dict.get("puzzle_json", "")

    if action == "upload_puzzle_meta_to_s3_from_json":
        response_message = upload_puzzle_meta_to_s3_from_json(puzzle_json_str)
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

    return {
        'messageVersion': '1.0',
        'response': function_response,
        'sessionAttributes': session_attributes,
        'promptSessionAttributes': prompt_session_attributes
    }
