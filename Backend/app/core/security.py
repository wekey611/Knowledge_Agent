from pwdlib import PasswordHash
password_hash = PasswordHash.recommended()

# hash
def get_password_hash(password):
    return password_hash.hash(password)
# verify hash
def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)