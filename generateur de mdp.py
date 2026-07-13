import random

print("Voici votre mot de passe : ")

caracteres = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTVWXYZ1234567890!@£<#¨`/;:?"
mdp = ""

for i in range(18):
    mdp += random.choice(caracteres)

print(mdp)
