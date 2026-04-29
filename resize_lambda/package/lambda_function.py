import boto3
import os
from io import BytesIO
from urllib.parse import unquote_plus
from PIL import Image

s3 = boto3.client("s3")

DEST_BUCKET = os.environ["DEST_BUCKET"]
MAX_SIZE = int(os.environ.get("MAX_SIZE", "800"))


def lambda_handler(event, context):
    for record in event["Records"]:
        source_bucket = record["s3"]["bucket"]["name"]
        source_key = unquote_plus(record["s3"]["object"]["key"])

        if not source_key.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            print(f"Skipping non-image file: {source_key}")
            continue

        if not source_key.startswith("originals/"):
            print(f"Skipping file outside originals/: {source_key}")
            continue

        response = s3.get_object(
            Bucket=source_bucket,
            Key=source_key
        )

        image_data = response["Body"].read()

        with Image.open(BytesIO(image_data)) as img:
            original_format = img.format or "JPEG"
            img.thumbnail((MAX_SIZE, MAX_SIZE))

            buffer = BytesIO()

            if original_format.upper() in ["JPEG", "JPG"]:
                img = img.convert("RGB")
                save_format = "JPEG"
                content_type = "image/jpeg"
            elif original_format.upper() == "PNG":
                save_format = "PNG"
                content_type = "image/png"
            elif original_format.upper() == "WEBP":
                save_format = "WEBP"
                content_type = "image/webp"
            else:
                img = img.convert("RGB")
                save_format = "JPEG"
                content_type = "image/jpeg"

            img.save(buffer, format=save_format)
            buffer.seek(0)

        file_name = source_key.split("/")[-1]

        s3.put_object(
            Bucket=DEST_BUCKET,
            Key=file_name,
            Body=buffer,
            ContentType=content_type
        )

        print(f"Resized {source_key} and saved to s3://{DEST_BUCKET}/{file_name}")

    return {
        "statusCode": 200,
        "message": "Image resize complete"
    }