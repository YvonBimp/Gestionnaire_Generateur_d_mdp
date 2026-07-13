import os
import sqlite3
import string
import secrets
from cryptography.fernet import Fernet

password_file = "password.key"

def generate_passw():
    if not os.path.exists(password_file):
        passw = Fernet.generate_key()
        with open(password_file, "wb") as fichier:
            fichier.write(passw)

def charger_passw():
    with open(password_file, "rb") as fichier:
        return fichier.read()

def intiale_passw():
    conn=sqlite3.connect("password.db")
    curr=conn.cursor()
    curr.execute("""
                CREATE TABLE IF NOT EXISTS passwords(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site TEXT NOT NULL,
                    login TEXT NOT NULL,
                    password TEXT NOT NULL)
                """)
    conn.commit()
    conn.close()
    initiale_passw()
def gener_mot_passw(longueur=16):
    alphabet = string.ascii_letters + string.digits+string.punctuation
    return "".join(secrets.choice(alphabet) for i in range(longueur))

generate_passw()
passw = charger_passw()
print("passw =", gener_mot_passw())