def verify_token(token: str) -> bool:
    # Dummy verifier for illustration. Replace with JWT check in prod.
    return token == "secure_token_123"