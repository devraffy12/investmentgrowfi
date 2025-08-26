import hashlib

SECRET_KEY = "86cb40fe1666b41eb0ad21577d66baef"

def make_md5_sign(params: dict, secret_key: str = SECRET_KEY) -> str:
    """
    Generate MD5 signature according to Galaxy API spec.
    """
    filtered = {k: v for k, v in params.items() if v and k != "sign"}
    sorted_items = sorted(filtered.items())
    query_str = "&".join([f"{k}={v}" for k, v in sorted_items])
    sign_str = f"{query_str}&key={secret_key}"
    return hashlib.md5(sign_str.encode("utf-8")).hexdigest()
