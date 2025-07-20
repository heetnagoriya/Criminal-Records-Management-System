import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CriminalRecords')

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))

        aadhar = body.get('aadhar')
        pan = body.get('pan')
        license_num = body.get('license')

        response = None
        item = None

        # 1. Search by aadhar (Primary Key)
        if aadhar:
            response = table.get_item(Key={'aadhar': aadhar})
            item = response.get('Item')

        # 2. Search by PAN using GSI
        elif pan:
            response = table.query(
                IndexName='PAN-index',
                KeyConditionExpression=Key('pan').eq(pan)
            )
            items = response.get('Items', [])
            item = items[0] if items else None

        # 3. Search by License using GSI
        elif license_num:
            response = table.query(
                IndexName='License-index',
                KeyConditionExpression=Key('license').eq(license_num)
            )
            items = response.get('Items', [])
            item = items[0] if items else None

        else:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({"error": "Provide either aadhar, pan, or license"})
            }

        if not item:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                "body": json.dumps({"message": "No record found"})
            }

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps(item)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({"error": "Internal error", "details": str(e)})
        }
