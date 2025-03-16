# S3
* S3_BUCKET_NAME = "word-puzzle-421"
* SOLUTIONS_FOLDER = "solutions/"

# Lambda Function
* See puzzle_manager.py for code
* CloudWatch logs: Log groups > /aws/lambda/puzzle_manager
  <img width="1217" alt="image" src="https://github.com/user-attachments/assets/60dd8537-e095-42cf-b6be-d01d148d926d" />

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


  
