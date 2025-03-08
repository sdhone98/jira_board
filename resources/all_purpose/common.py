import re
import bcrypt
from resources.all_purpose import constant

rounds = constant.BCRYPT_ROUNDS
algo = constant.BCRYPT_ALGORITHM
email_regex = constant.EMAIL_REGEX

def convert_raw_password_to_hash(raw_password: str) -> bytes:
    user_pass = raw_password.encode("utf-8")
    hashed_pass = bcrypt.hashpw(user_pass, bcrypt.gensalt(rounds, algo))
    return hashed_pass


def email_validator(email):
    return True if re.match(email_regex, email) else False
