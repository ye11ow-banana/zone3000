import secrets


def generate_redirect_identifier() -> str:
    return secrets.token_urlsafe(6)
