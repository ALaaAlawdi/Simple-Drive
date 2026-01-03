import hashlib
import hmac
import datetime
import requests
from urllib.parse import urlencode

from app.core.config import settings
from app.core.logger import setup_logger
from dotenv import load_dotenv
import os

load_dotenv()

logger = setup_logger(__name__)

ACCESS_KEY = os.getenv("S3_ACCESS_KEY") or settings.S3_ACCESS_KEY #
SECRET_KEY =os.getenv("S3_SECRET_KEY") or settings.S3_SECRET_KEY # 
REGION = os.getenv("S3_REGION") or settings.S3_REGION
BUCKET = settings.S3_BUCKET


ENDPOINT = f"s3.{REGION}.amazonaws.com"
SERVICE = "s3"


# AWS Signature Version 4
def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def get_signature_key(key, date_stamp, region_name, service_name):
    if not all([key, date_stamp, region_name, service_name]):
        raise ValueError("Invalid parameters for signature key generation")

    k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
    k_region = sign(k_date, region_name)
    k_service = sign(k_region, service_name)
    return sign(k_service, "aws4_request")


def s3_request(
    method: str,
    object_key: str = "",
    data: bytes = b"",
    params: dict | None = None,
):
    logger.info(
        f"S3 request started | method={method} "
        f"object_key={object_key} payload_size={len(data)}"
    )

    try:
        t = datetime.datetime.now(datetime.timezone.utc)
        amz_date = t.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = t.strftime("%Y%m%d")

        

        if not ACCESS_KEY or not SECRET_KEY or not REGION or not BUCKET:
            logger.critical("Missing AWS configuration")
            raise RuntimeError("AWS configuration incomplete")

        

        canonical_uri = f"/{BUCKET}/"
        if object_key:
            canonical_uri += object_key

        canonical_query_string = ""
        if params:
            canonical_query_string = urlencode(sorted(params.items()))

        url = f"https://{ENDPOINT}{canonical_uri}"
        if canonical_query_string:
            url += f"?{canonical_query_string}"

        payload_hash = hashlib.sha256(data).hexdigest()

        logger.debug(f"Request URL: {url}")
        logger.debug(f"Canonical URI: {canonical_uri}")
        logger.debug(f"Payload SHA256: {payload_hash}")
        logger.debug(f"AMZ Date: {amz_date}")

        canonical_headers = (
            f"host:{ENDPOINT}\n"
            f"x-amz-content-sha256:{payload_hash}\n"
            f"x-amz-date:{amz_date}\n"
        )

        signed_headers = "host;x-amz-content-sha256;x-amz-date"

        canonical_request = (
            f"{method}\n"
            f"{canonical_uri}\n"
            f"{canonical_query_string}\n"
            f"{canonical_headers}\n"
            f"{signed_headers}\n"
            f"{payload_hash}"
        )

        credential_scope = f"{date_stamp}/{REGION}/{SERVICE}/aws4_request"
        string_to_sign = (
            f"AWS4-HMAC-SHA256\n"
            f"{amz_date}\n"
            f"{credential_scope}\n"
            f"{hashlib.sha256(canonical_request.encode()).hexdigest()}"
        )

        logger.debug("Canonical Request:")
        logger.debug(canonical_request)

        logger.debug("String To Sign:")
        logger.debug(string_to_sign)

        signing_key = get_signature_key(SECRET_KEY, date_stamp, REGION, SERVICE)
        signature = hmac.new(
            signing_key, string_to_sign.encode(), hashlib.sha256
        ).hexdigest()

        headers = {
            "x-amz-date": amz_date,
            "x-amz-content-sha256": payload_hash,
            "Authorization": (
                f"AWS4-HMAC-SHA256 "
                f"Credential={ACCESS_KEY}/{credential_scope}, "
                f"SignedHeaders={signed_headers}, "
                f"Signature={signature}"
            ),
        }

        response = requests.request(method, url, headers=headers, data=data)

        logger.info(f"S3 response status: {response.status_code}")

        if response.status_code >= 400:
            logger.error("S3 error response body:")
            logger.error(response.text)

        return response

    except Exception as e:
        logger.exception(f"Unhandled exception during S3 request: {e}")
        raise
