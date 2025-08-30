import secrets

# Generate a 32-byte secret key (64-character hex string)
secret_key = secrets.token_hex(32)

print(secret_key)