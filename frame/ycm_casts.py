from frame.config import cfg
from frame.cert import download_cert


def prepend_https(url: str):
    return f"https://{url}"


def s3_or_local(path: str):
    if not path.startswith("s3://"):
        return path
    path = path[len("s3://") :]
    return download_cert(
        cfg.s3.endpoint_url(cast=prepend_https),
        cfg.s3.access_key(),
        cfg.s3.secret_key(),
        cfg.s3.bucket(),
        cfg.s3.cert(),
    )
