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
	call(ffmpeg_path + ' -framerate 8 -pattern_type glob -i "*.jpg" -vcodec h264 -acodec aac -strict -2 -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" ' + _filepath(outfilename), shell=True)

def upload_vid_s3(outfilename):
	s3.Object(bucketname, outfilename).upload_file(_filepath(outfilename), ExtraArgs={'ACL':'public-read'})

def cleanup(filelist, outfilename):
	remove(_filepath(outfilename))
	for filename in filelist:
		remove(_filepath(filename))

def lambda_handler(event, context):
	filelist = event["filelist"]
	outfilename = event["outfilename"]
	print "Generating", outfilename
	print "Downloading", len(filelist), "files from S3"
	download_files_s3(filelist)
	print "Download done. Processing video"
	process_video(outfilename)
	if path.isfile(_filepath(outfilename)):
		print "Video generated!"
		upload_vid_s3(outfilename)
		print "Video uploaded;"
		delete_files_s3(filelist)
		print "Source jpegs deleted from s3."
		print "Job completed."
		return "Success!"
	cleanup(filelist, outfilename)

# Note: This requires ffmpeg, packed in using the following lib
# https://intoli.com/blog/transcoding-on-aws-lambda/
