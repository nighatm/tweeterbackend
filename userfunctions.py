import random
import string
import mariadb
import dbcreds

# get random string password with letters, digits, and symbols
def get_random_password_string(length):
    password_characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(password_characters) for i in range(length))
    return password
    # print("Random string password is:", password)

def login(username, password):
    conn = None
    cursor = None
    row = None
    try:
        conn = mariadb.connect(host=dbcreds.host, port=dbcreds.port,user=dbcreds.user, password=dbcreds.password,database=dbcreds.database)
        cursor=conn.cursor()
        