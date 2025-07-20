import boto3
import json

dynamodb = boto3.client('dynamodb')

def lambda_handler(event, context):
    body = event.get("queryStringParameters", {}) or json.loads(event.get("body", "{}"))
    user_id = body.get("userId")
    password = body.get("password")

    if not user_id or not password:
        return {
            "statusCode": 400,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({"message": "userId and password are required"})
        }

    try:
        response = dynamodb.get_item(
            TableName='Users',
            Key={'userId': {'S': user_id}}
        )

        item = response.get("Item")

        if item is None:
            return {
                "statusCode": 401,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps({"message": "Invalid credentials"})
            }

        stored_password = item.get("password", {}).get("S", "")

        if password == stored_password:
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps({"message": "Login successful"})
            }
        else:
            return {
                "statusCode": 403,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps({"message": "Invalid password"})
            }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({"message": "Internal Server Error", "error": str(e)})
        }
