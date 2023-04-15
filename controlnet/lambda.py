import boto3, json, base64, io, urllib, time
from pathlib import Path
from botocore.exceptions import ClientError
from PIL import Image
import datetime

ENDPOINT_NAME = "controlnet-logos-endpoint"
SENDER = "fra.pochetti@gmail.com"
CHARSET = "UTF-8"
SES = boto3.client('ses', region_name="eu-west-1")
S3 = boto3.client('s3')
sm_runtime = boto3.Session().client(service_name='sagemaker-runtime')
SUBJECT = "VisualNeurons.com - your logo has been uploaded!"
BODY_TEXT = ("VisualNeurons.com - your logo has been uploaded! \r\n"
                "The purpose of this email is to confirm that we successfully ingested your file"
                "and that we are currently processing it."
            )
BODY_HTML = """
<html>

<head></head>

<body>
    <h4>You just uploaded your logo to our servers. Congratulations!</h4>
    <p>The purpose of this email is to confirm that we successfully ingested your file and that we are currently processing it.
        <br>
        When our AI artists are done with it, you'll receive another email with a link to a zip file containing a bunch of original and creative versions of your logo.
        <br>
        This might take up to one hour. Thanks for your patience!
    </p>
</body>

</html>
"""


def format_response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }


def send_email_to_user(recipient):
    try:
        response = SES.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(f"Email sent to {recipient}! Message ID: {response['MessageId']}")
    return


def lambda_handler(event, context):
    
    now = datetime.datetime.now()
    now_path = f"{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}"

    record = event['Records'][0]
    upload_bucket = record['s3']['bucket']['name']
    upload_key = record['s3']['object']['key']
    s3_upload_location = f"s3://{upload_bucket}/{upload_key}"
    print(f"Upload location {s3_upload_location}")
    
    response = S3.head_object(Bucket=upload_bucket, Key=upload_key)
    recipient = response['Metadata']['email']
    print(f"Email: {recipient}")
    
    data = {"img_id": s3_upload_location}
    data_stream = io.BytesIO()
    S3.download_fileobj(upload_bucket, upload_key, data_stream)
    img_data = base64.b64encode(data_stream.getvalue())

    sm_input_bucket = "visualneurons.com-logos-outputs"
    sm_input_key = upload_key.split("/")
    sm_input_key = f"{sm_input_key[0]}/{now_path}/input/{sm_input_key[1].split('.')[0]}.json"

    data["img_data"] = img_data.decode("utf-8")
    data["email"] = recipient
    data["s3_location"] = f"{sm_input_key[0]}/{now_path}/output/"
    
    S3.put_object(
        Body=json.dumps(data),
        Bucket=sm_input_bucket,
        Key=sm_input_key,
        ContentType="application/json",
    )
    
    s3_input_location = f"s3://{sm_input_bucket}/{sm_input_key}"
    print(f"SageMaker input location {s3_input_location}")
    
    response = sm_runtime.invoke_endpoint_async(EndpointName=ENDPOINT_NAME, InputLocation=s3_input_location)
    s3_output_location = response["OutputLocation"]
    print(f"SageMaker output location {s3_output_location}")

    send_email_to_user(recipient)
    
    return format_response(s3_output_location, 200)