# import hashlib
# import hmac
# import datetime
# import requests
# import os 
# from dotenv import load_dotenv
# load_dotenv()

# # 1. Update these to match your bucket's actual location
# ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
# SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
# REGION = 'eu-north-1'  # CHANGE THIS to your bucket's actual region
# ENDPOINT = f's3.{REGION}.amazonaws.com'  # Use regional endpoint to avoid 301
# BUCKET = os.getenv('S3_BUCKET')

# def sign(key, msg):
#     return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

# def get_signature_key(key, date_stamp, region_name, service_name):
#     k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
#     k_region = sign(k_date, region_name)
#     k_service = sign(k_region, service_name)
#     k_signing = sign(k_service, 'aws4_request')
#     return k_signing

# def s3_request(method, object_key, data=b""):
#     service = 's3'
#     # Fixed DeprecationWarning: use datetime.UTC
#     t = datetime.datetime.now(datetime.UTC)
#     amz_date = t.strftime('%Y%m%dT%H%M%SZ')
#     date_stamp = t.strftime('%Y%m%d')

#     canonical_uri = f'/{BUCKET}/{object_key}'
#     url = f'https://{ENDPOINT}{canonical_uri}'
    
#     payload_hash = hashlib.sha256(data).hexdigest()
#     canonical_headers = f'host:{ENDPOINT}\nx-amz-content-sha256:{payload_hash}\nx-amz-date:{amz_date}\n'
#     signed_headers = 'host;x-amz-content-sha256;x-amz-date'
    
#     canonical_request = (
#         f'{method}\n{canonical_uri}\n\n'
#         f'{canonical_headers}\n{signed_headers}\n{payload_hash}'
#     )

#     credential_scope = f'{date_stamp}/{REGION}/{service}/aws4_request'
#     string_to_sign = (
#         f'AWS4-HMAC-SHA256\n{amz_date}\n{credential_scope}\n'
#         f'{hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()}'
#     )

#     signing_key = get_signature_key(SECRET_KEY, date_stamp, REGION, service)
#     signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

#     authorization_header = (
#         f'AWS4-HMAC-SHA256 Credential={ACCESS_KEY}/{credential_scope}, '
#         f'SignedHeaders={signed_headers}, Signature={signature}'
#     )

#     headers = {
#         'x-amz-date': amz_date,
#         'x-amz-content-sha256': payload_hash,
#         'Authorization': authorization_header,
#         'Content-Length': str(len(data)) if method == 'PUT' else '0'
#     }

#     if method == 'PUT':
#         resp = requests.put(url, data=data, headers=headers)
#     else:
#         resp = requests.get(url, headers=headers)
    
#     # If still getting 301, this will show the correct endpoint suggested by S3
#     if resp.status_code == 301:
#         print(f"DEBUG 301 Error Response: {resp.text}")
        
#     return resp

# # Usage remains the same
# object_name = 'requirements.txt'
# content = b'requests\nhttpx'

# put_res = s3_request('PUT', object_name, data=content)
# print(f"PUT Status: {put_res.status_code}")

# get_res = s3_request('GET', object_name)
# print(f"GET Status: {get_res.status_code}")
# if get_res.status_code == 200:
#     print(f"Content: {get_res.text}")

from ftplib import FTP_TLS
from io import BytesIO
import ssl

context = ssl._create_unverified_context()

ftp = FTP_TLS()
ftp.context = context

ftp.connect("127.0.0.1", 21, timeout=10)

# Explicit FTPS (important)
ftp.auth()
ftp.prot_p()

ftp.login("test", "A104494045Aa#")
ftp.set_pasv(True)
ftp.cwd("/")

# ---- create text content ----
content = "Hello from Python via FTPS!\nThis file should NOT be empty."
data = content.encode("utf-8")

# ---- upload ----
buffer = BytesIO(data)
buffer.seek(0)  # 🔴 THIS LINE FIXES ZERO-BYTE FILES

ftp.storbinary("STOR fixed_upload.txt", buffer)

ftp.quit()

print("✅ File uploaded with content")
