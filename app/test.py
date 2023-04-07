import random
import string
def generate_user_id():
    return ''.join(random.choices(string.hexdigits, k=16))

val=generate_user_id()
