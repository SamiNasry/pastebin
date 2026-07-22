import secrets

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
ID_LENGTH = 8
TOKEN_LENGTH = 32

def generate_id() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(ID_LENGTH))


def generate_delete_token() -> str:
    return secrets.token_urlsafe(TOKEN_LENGTH)
