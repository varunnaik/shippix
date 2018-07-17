import boto3
import json

s3 = boto3.resource('s3')
client = boto3.client('lambda')

lambdaarn = 'arn:aws:lambda:ap-southeast-2:807832556430:function:imagesToVideo'

for file in filelist:
	filekey = file.split('_')[0]

	if (filekey in jobs) {
		jobs[filekey] = []
	}
	jobs[filekey].append(file)


for filekey in jobs:
	        client.invoke(FunctionName=lambdaarn,
                         InvocationType='RequestResponse',
                         Payload=json.dumps({"filelist": jobs[filekey].sort(), "outfilename": str(filekey) + ".avi"}))
        print "Invoke", self.captureimages[code], str(code)