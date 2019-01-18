import json
import boto3
import logging
import os
import time
import subprocess
import shutil

s3 = boto3.resource('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
def lambda_handler(event, context):

    obj_key = event['Records'][0]['s3']['object']['key']
    src_bucket = event['Records'][0]['s3']['bucket']['name']
    target_bucket = 'python-lambda-gifs'
    
    
    # Copy objkey to /tmp
    bucket = s3.Bucket(src_bucket)
    bucket.download_file(obj_key,'/tmp/'+obj_key)

    # Copy ffmpeg to tmp and chmod it
    # check if container is being reused, if so ffmpeg is alreaady there
    if not os.path.exists('/tmp/ffmpeg'):
        shutil.copyfile('/var/task/bin/ffmpeg','/tmp/ffmpeg') 
        os.chmod('/tmp/ffmpeg',0o755)

    #Run ffmpeg
    path_to_video = '/tmp/'+obj_key
    target_filename = os.path.splitext(obj_key)[0] + time.strftime("%Y%m%d-%H%M%S") + ".gif"
    target_fullname = '/tmp/'+target_filename
    args = '/tmp/ffmpeg -t 45 -ss 00:00:3 -i ' + path_to_video + ' -filter_complex fps=10,scale=w=360:h=-2,setpts=0.125*PTS ' + target_fullname + ' -y'
    args = args.split()
    popen = subprocess.Popen(args,stdout=subprocess.PIPE)
    popen.wait()

    # Upload gif to target bucket
    bucket = s3.Bucket(target_bucket)
    
    bucket.upload_file(target_fullname,target_filename)

    return {
        'statusCode': 200,
        'body': json.dumps('Gif Created!')
    }
