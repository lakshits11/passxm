import random
import string

def generatePassword(length):
    # Generate a random password of length 'length' containing uppercase and lowercase letters, digits and special characters
   return "".join(random.choices(string.ascii_letters + string.ascii_lowercase + string.digits + string.punctuation, k=length))
