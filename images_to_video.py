import boto3
from os import remove, chdir, path
from subprocess import call

s3 = boto3.resource('s3')
bucketname = 'shippix'
bucketdir = 'img/'

def _filepath(filename):
	return '/tmp/'+filename

def download_files_s3(filelist):
	for filename in filelist:
		s3.Object(bucketname, bucketdir + filename).download_file(_filepath(filename))

def delete_files_s3(filelist):
	for filename in filelist:
		s3.Object(bucketname, bucketdir + filename).delete()

def process_video(outfilename):
	ffmpeg_path = path.dirname(path.realpath(__file__)) + "/bin/ffmpeg"
	chdir('/tmp')
	#call([ffmpeg_path, "-framerate", "8", "-pattern_type", "glob", "-i", "'*.jpg'", _filepath(outfilename)])
	call(ffmpeg_path + " -framerate 8 -pattern_type glob -i '*.jpg' " + _filepath(outfilename), shell=True)

def upload_vid_s3(outfilename):
	s3.Object(bucketname, outfilename).upload_file(_filepath(outfilename))

def cleanup(filelist, outfilename):
	remove(_filepath(outfilename))
	for filename in filelist:
		remove(_filepath(filename))

def lambda_handler(event, context):
	filelist = event["filelist"]
	outfilename = event["outfilename"]
	download_files_s3(filelist)
	process_video(outfilename)
	if path.isfile(_filepath(outfilename)):
		delete_files_s3(filelist)
		upload_vid_s3(outfilename)
		return "Success!"
	cleanup(filelist, outfilename)

# Note: This requires ffmpeg, packed in using the following lib
# https://intoli.com/blog/transcoding-on-aws-lambda/
