import os
import sqlite3
import string
import secrets
import time
from cryptography.fernet import Fernet
import pyperclip
from threading import Timer

password_file = "password.key"
db_file = "password.db"
CLIPBOARD_CLEAR_DELAY = 10  # secondes avant de nettoyer le presse-papier


def generate_key():
    if not os.path.exists(password_file):
        key = Fernet.generate_key()
        with open(password_file, "wb") as f:
            f.write(key)


def charger_key():
    with open(password_file, "rb") as f:
        return f.read()


def initialiser_db():
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS passwords(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site TEXT NOT NULL,
            login TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def generer_mot_de_passe(longueur=16):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(longueur))


def masquer_mot_de_passe(password):
    return "*" * len(password)


def clear_clipboard():
    try:
        # méthode simple et portable : copier une chaîne vide
        pyperclip.copy("")
    except Exception:
        pass


def copier_et_nettoyer(mdp):
    try:
        pyperclip.copy(mdp)
        # lance un timer pour nettoyer le presse-papier après CLIPBOARD_CLEAR_DELAY secondes
        t = Timer(CLIPBOARD_CLEAR_DELAY, clear_clipboard)
        t.daemon = True
        t.start()
    except Exception:
        print("Impossible de copier dans le presse-papier (pyperclip).")


def ajouter_mot_passw(site, login, password, fernet):
    encrypted = fernet.encrypt(password.encode()).decode()
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO passwords (site, login, password) VALUES (?, ?, ?)",
        (site, login, encrypted)
    )
    conn.commit()
    conn.close()

    copier_et_nettoyer(password)
    print(f"Mot de passe pour {site} enregistré : {masquer_mot_de_passe(password)} (copié dans le presse-papier pour {CLIPBOARD_CLEAR_DELAY}s).")


def liste_mot_passw():
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT site, login FROM passwords")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        print("Pas de données.")
    else:
        print("Liste des mots de passe :")
        for site, login in rows:
            print(f"Site: {site} | Login: {login} | Password: ************")


def rechercher_mot_passw(requete, fernet):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute(
        "SELECT site, login, password FROM passwords WHERE site LIKE ?",
        (f"%{requete}%",)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        print("Aucun résultat.")
    else:
        site, login, password_enc = row
        try:
            mot_de_passe = fernet.decrypt(password_enc.encode()).decode()
        except Exception:
            print("Erreur lors du déchiffrement.")
            return
        copier_et_nettoyer(mot_de_passe)
        print(f"Mot de passe pour {site} : {masquer_mot_de_passe(mot_de_passe)} (copié dans le presse-papier pour {CLIPBOARD_CLEAR_DELAY}s).")


def menu_ajout(fernet):
    print("\nAjouter un mot de passe :")
    site = input("Entrez le site : ").strip()
    login = input("Entrez le login : ").strip()

    while True:
        choix = input("Voulez-vous (1) rentrer votre mot de passe ou (2) le générer automatiquement ? [1/2] : ").strip()
        if choix == "1":
            password = input("Entrez votre mot de passe (sera masqué à l'affichage) : ")
            break
        elif choix == "2":
            try:
                longueur = int(input("Longueur du mot de passe (par défaut 16) : ") or "16")
            except ValueError:
                longueur = 16
            password = generer_mot_de_passe(longueur)
            break
        else:
            print("Choix invalide, entrez 1 ou 2.")

    ajouter_mot_passw(site, login, password, fernet)


def main():
    generate_key()
    fernet = Fernet(charger_key())
    initialiser_db()

    while True:
        print("\nOptions : (g)énérer/ajouter  (l)ister  (r)echercher  (q)uitter")
        choix = input("Entrez votre choix : ").lower().strip()
        if choix == "g":
            menu_ajout(fernet)
        elif choix == "l":
            liste_mot_passw()
        elif choix == "r":
            requete = input("Mot-clé : ").strip()
            rechercher_mot_passw(requete, fernet)
        elif choix == "q":
            print("Au revoir.")
            break
        else:
            print("Choix inconnu.")


if __name__ == "__main__":
    main()