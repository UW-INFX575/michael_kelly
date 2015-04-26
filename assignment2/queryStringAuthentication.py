from boto.s3.connection import S3Connection
from boto.s3.key import Key
import os.path

# Specify S3 Bucket and AWS Credentials
bucket_name = '<bucket-name>'
access_key = '<access-key>'
secret_key = '<secret-key>'

# Specify source and destination for files
sourceDir = 'output/' # local
destDir = 'ngram-output/' # S3

# Set expiration on S3 signature links 
link_expiration_time = 60*60*24*30 # 30 days

# Connect to bucket
conn = S3Connection(access_key, secret_key)
bucket = conn.get_bucket(bucket_name)

qsa_urls = [] 
uploadFileNames = []

# Gather files to upload from source directory
for (sourceDir, dirname, filename) in os.walk(sourceDir):
    uploadFileNames.extend(filename)
    break

# Upload to S3
print 'Uploading ngram files to Amazon S3 bucket %s' % bucket_name
for filename in uploadFileNames:
    sourcepath = os.path.join(sourceDir + filename)
    destpath = os.path.join(destDir, filename)
     
    # Create new key in bucket and upload file to path
    k = Key(bucket)
    k.key = destpath
    k.set_contents_from_filename(sourcepath)
    
    # Make access to file private unless signature link is used
    k.set_canned_acl('private')
    qsa_urls.append(k.generate_url(link_expiration_time))

print 'Upload complete. Signature URLs for files: '
for url in qsa_urls:
    print url