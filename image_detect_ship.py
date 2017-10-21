import boto3

client = boto3.client('rekognition')

response = client.detect_labels(
    Image=Buffer,
    MaxLabels=50,
    MinConfidence=70,
)

