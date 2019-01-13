import boto3
from os import remove, chdir, path, stat, listdir
from subprocess import call

s3 = boto3.resource('s3')
bucketname = 'shippix'
bucketdir = 'img/'

def _filepath(filename):
	return '/tmp/'+filename

def download_files_s3(filelist):
	for filename in filelist:
		print _filepath(filename)
		s3.Object(bucketname, bucketdir + filename).download_file(_filepath(filename))

def delete_files_s3(filelist):
	for filename in filelist:
		s3.Object(bucketname, bucketdir + filename).delete()

def process_video(outfilename):
	ffmpeg_path = path.dirname(path.realpath(__file__)) + "/bin/ffmpeg"
	chdir('/tmp')
	# -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2"
	call(ffmpeg_path + ' -framerate 10 -pattern_type glob -i "*.jpg" -vcodec h264 -an -y ' + _filepath(outfilename), shell=True)

def upload_vid_s3(outfilename):
	s3.Object(bucketname, 'video/'+outfilename).upload_file(_filepath(outfilename), ExtraArgs={'ACL':'public-read'})

def upload_thumb_s3(outfilename, filelist):
	s3.Object(bucketname, 'thumb/'+outfilename.replace('.mp4', '.jpg')).upload_file(_filepath(filelist[0]), ExtraArgs={'ACL':'public-read'})

def cleanup(filelist, outfilename):
	remove(_filepath(outfilename))
	for filename in filelist:
		remove(_filepath(filename))
 
def lambda_handler(event, context):
	filelist = event["filelist"]
	outfilename = event["outfilename"]
	print "Generating", outfilename
	print "Downloading", len(filelist), "files from S3"
	print "Disk contains", listdir('/tmp/')
	download_files_s3(filelist)
	print "Download done. Processing video"
	process_video(outfilename)
	if path.isfile(_filepath(outfilename)) and stat(_filepath(outfilename)).st_size > 100:
		print "Video generated!", stat(_filepath(outfilename)).st_size
		upload_vid_s3(outfilename)
		upload_thumb_s3(outfilename, filelist)
		print "Video uploaded;"
		if "preservesource" not in event:
			delete_files_s3(filelist)
			print "Source jpegs deleted from s3."
		print "Job completed."
	cleanup(filelist, outfilename)

# Note: This requires ffmpeg, packed in using the following lib
# https://intoli.com/blog/transcoding-on-aws-lambda/
