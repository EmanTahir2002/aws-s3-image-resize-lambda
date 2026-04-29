import boto3
import os

s3 = boto3.client("s3")

BUCKET = os.environ["BUCKET"]


def lambda_handler(event, context):
    deleted_count = 0

    paginator = s3.get_paginator("list_objects_v2")

    for page in paginator.paginate(Bucket=BUCKET):
        objects = page.get("Contents", [])

        if not objects:
            continue

        delete_batch = {
            "Objects": [{"Key": obj["Key"]} for obj in objects]
        }

        s3.delete_objects(
            Bucket=BUCKET,
            Delete=delete_batch
        )

        deleted_count += len(objects)

    print(f"Deleted {deleted_count} objects from bucket: {BUCKET}")

    return {
        "statusCode": 200,
        "bucket": BUCKET,
        "deleted_count": deleted_count,
        "message": "Bucket emptied successfully"
    }