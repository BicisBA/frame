import pathlib
import tempfile

import boto3


def download_cert(
    endpoint_url: str, access_key: str, secret_key: str, bucket: str, prefix: str
) -> str:
    filename = prefix.split("/")[-1]
    cert_location = str(pathlib.Path().joinpath(tempfile.gettempdir(), filename))

    minio = boto3.resource(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        verify=False,
    )
    minio.Bucket(bucket).Object(prefix).download_file(cert_location)

    return str(cert_location)
