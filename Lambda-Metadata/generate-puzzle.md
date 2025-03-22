* Lambda function name: word-puzzle-421-v2-generate-meta
    * Corresponding action group: ag-word-puzzle-generate-meta
* Time out limit: 2 min
* Permissions
    * Add S3 full access
    * Add Bedrock full acess
* Resource-based policy
```
aws lambda add-permission \
    --function-name word-puzzle-421-v2-generate-meta \
    --statement-id bedrock-invoke-generate-puzzle-meta \
    --action "lambda:InvokeFunction" \
    --principal "bedrock.amazonaws.com" \
    --source-arn "arn:aws:bedrock:<REGION>:<YOUR_ACCOUNT_ID>:*" \
    --region us-east-1
```

```
{
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {
      "Sid": "bedrock-invoke-generate-puzzle-meta",
      "Effect": "Allow",
      "Principal": {
        "Service": "bedrock.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:<REGION>:<YOUR_ACCOUNT_ID>:function:word-puzzle-421-v2-generate-meta",
      "Condition": {
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:bedrock:<REGION>:<YOUR_ACCOUNT_ID>:*"
        }
      }
    }
  ]
}
```