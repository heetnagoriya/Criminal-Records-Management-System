import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CriminalRecords')

def lambda_handler(event, context):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        "Access-Control-Allow-Headers": "*"
    }

    try:
        raw_body = event.get("body", {})
        body = raw_body if isinstance(raw_body, dict) else json.loads(raw_body)

    
        print("Parsed Body:", body)

      
        aadhar = body.get("aadhar")
        name = body.get("name")
        dob = body.get("dob")
        pan = body.get("pan")
        license_num = body.get("license")
        crime = body.get("crime") or body.get("newFIR")

        if not (aadhar and name and dob and pan and license_num and crime):
            return {
                "statusCode": 400,
                "headers": headers,
                "body": json.dumps({
                    "message": "All fields are required (aadhar, name, dob, pan, license, crime).",
                    "received": body  
                })
            }

        # Check if criminal record already exists
        response = table.get_item(Key={"aadhar": aadhar})
        item = response.get("Item")

        if item:
            # Append the new crime to existing list
            existing_crimes = item.get("crimes", [])
            existing_crimes.append(crime)

            table.update_item(
                Key={"aadhar": aadhar},
                UpdateExpression="SET crimes = :c",
                ExpressionAttributeValues={":c": existing_crimes}
            )

            return {
                "statusCode": 200,
                "headers": headers,
                "body": json.dumps({"message": "FIR added to existing record"})
            }

        else:
            
            table.put_item(
                Item={
                    "aadhar": aadhar,
                    "name": name,
                    "dob": dob,
                    "pan": pan,
                    "license": license_num,
                    "crimes": [crime]
                }
            )

            return {
                "statusCode": 201,
                "headers": headers,
                "body": json.dumps({"message": "New record created with FIR"})
            }

    except Exception as e:
        print("Exception occurred:", str(e))
        return {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({"message": "Internal server error", "error": str(e)})
        }
