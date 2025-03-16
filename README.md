# AWS Bedrock Word Puzzle

## High Level Summary

* This is a mini project to build an agentic flow to create and evaluate a mini word puzzle.
* High level spec
    * Word Puzzle: Guess 1 word based on 4 descriptions. It's a simplified version of 4-images-1-word puzzles.
    * AWS setup:
       * S3 for puzzle storage
       * Lambda function for tool calling
       * Claude 3.5 Sonnet as LLM (note that LLM models do not support tool use)
* Folder organization
  * console: AWS Console UI components
  * local: Bedrock API calls given the AWS Console setup
 
##  Trouble shoot

### IAM
* Lambda Function need access to Get and Put S3 objects: policy `AmazonS3FullAccess` is attached to role `puzzle_manager-role-2clfko0l`
* Bedrock Agent need access to invoke Lambda Functions: attach policy `AWSLambda_FullAccess` to `AmazonBedrockExecutionRoleForAgents_PP0U8PI3IUH`
```
  {
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {
      "Sid": "bedrock-invoke",
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:<REGION>:<YOUR_ACCOUNT_ID>:function:<LAMBDA_FUNCTION_NAME>",
      "Condition": {
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:bedrock:<REGION>:<YOUR_ACCOUNT_ID>:*"
        }
      }
    }
  ]
}
```

### Lambda Function Debug
* Input: Lambda gets different input during testing vs. when triggered by Bedrock. So it's possible the Lambda test is successful but Bedrock invoking Lambda is not.
  * Add logging in Lambda function to examine input format
  * Use CloudWatch to examine the logs as Bedrock invokes Lambda
* Output: Even when the task is completed successfully, Bedrock agent may still throw the error `The server encountered an error processing the Lambda response. Check the Lambda response and retry the request`. Solution: [Action group Lambda function example > Function details](https://docs.aws.amazon.com/bedrock/latest/userguide/agents-lambda.html#agents-lambda-example)
