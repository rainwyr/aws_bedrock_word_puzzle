import boto3
import json
import logging
import os
import base64

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")

BUCKET_NAME = "word-puzzle-421"
MODEL_ID = "amazon.titan-image-generator-v2:0"  # Built-in for Titan via Bedrock

def generate_image(description):
    logger.info(f"Generating image for: {description}")
    
    payload = {
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": description
        }
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(payload)
    )

    response_body = json.loads(response['body'].read())
    base64_image = response_body.get("images", [None])[0]
    return base64.b64decode(base64_image) if base64_image else None

def upload_image_to_s3(image_bytes, image_key):
    logger.info(f"Uploading image to S3 at images/{image_key}")
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=f"images/{image_key}",
        Body=image_bytes,
        ContentType='image/png'
    )

def retrieve_and_generate_images(target_word):
    try:
        logger.info(f"Fetching puzzle for target word: {target_word}")
        key = f"solutions_by_word/{target_word}.json"
        response = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        puzzle = json.loads(response['Body'].read())

        descriptions = puzzle["descriptions"]
        image_urls = puzzle["image_urls"]

        for i in ["1", "2", "3", "4"]:
            description = descriptions.get(i)
            image_key = image_urls.get(i)

            if not description or not image_key:
                logger.warning(f"Skipping incomplete pair {i}")
                continue

            image_data = generate_image(description)
            if image_data:
                upload_image_to_s3(image_data, image_key)
            else:
                logger.warning(f"Failed to generate image for description {i}")

        return f"✅ Images generated and uploaded for '{target_word}'"

    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return f"❌ Failed to generate images: {str(e)}"

def lambda_handler(event, context):
    logger.info(f"Full event: {json.dumps(event, indent=2)}")

    action = event.get('function', '').strip()
    parameters = event.get('parameters', [])
    param_dict = {param["name"]: param["value"] for param in parameters}

    target_word = param_dict.get("target_word", "")

    if action == "generate_images_for_word":
        response_message = retrieve_and_generate_images(target_word)
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

    return {
        'messageVersion': '1.0',
        'response': function_response,
        'sessionAttributes': event.get('sessionAttributes', {}),
        'promptSessionAttributes': event.get('promptSessionAttributes', {})
    }
