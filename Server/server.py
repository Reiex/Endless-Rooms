# -*- coding:utf-8 -*

import hashlib
from datetime import datetime
from os import listdir, mkdir, getcwd
import socket
import sqlite3 as sql

# Création / Ouverture de la base de donnée et des tables

if "data" not in listdir(getcwd()):
    mkdir(getcwd()+"/data")

DATABASE = sql.connect("data/data.db")
CURSOR = DATABASE.cursor()
CURSOR.execute("CREATE TABLE IF NOT EXISTS LEVELS("
               "ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, "
               "NOM TEXT, "
               "NIVEAU BLOB)")
DATABASE.commit()
CURSOR.execute("CREATE TABLE IF NOT EXISTS USERS("
               "ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, "
               "NOM TEXT, "
               "PASSWORD TEXT)")
DATABASE.commit()

SEPERATEUR_ITEM = "*ITEM*"
SEPERATEUR_ELEMENT = "*ELEMENT*"


# Fonction qui permet d'obtenir la réponse du serveur

def recevoir(connexion):

    chaine = b""
    while chaine[-5:] != b"*End*":
        chaine += connexion.recv(1024)

    chaine = chaine[:-5].decode()
    return {key: value for key, value in [item.split(SEPERATEUR_ITEM) for item in chaine.split(SEPERATEUR_ELEMENT)]}

# Fonction qui permet d'envoyer une demande au serveur

def envoyer(connexion, dictionnaire_a_envoyer):

    chaine = SEPERATEUR_ELEMENT.join([SEPERATEUR_ITEM.join(item) for item in dictionnaire_a_envoyer.items()])
    connexion.send(chaine.encode()+b"*End*")

# Création et connexion du serveur

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("", 25099))

# ----------------------------------------------------------------------------------------------------------------------
# BOUCLE DU SERVEUR
# ----------------------------------------------------------------------------------------------------------------------

while True:

    print("Serveur en attente d'une connexion...")

    try:

        # Accepter la connexion d'un client et obtenir sa demande

        server.listen(5)
        connexion, adresse = server.accept()
        connexion.settimeout(1.0)

        heure = datetime.now()
        moment_connexion = "["+str(heure.hour)+":"+str(heure.minute)+":"+str(heure.second)+"]"
        chaine_nouvelle_connexion = moment_connexion+" - Nouvelle connexion:"+adresse[0]+"\nAttente d'une demande..."
        print(chaine_nouvelle_connexion)

        demande = recevoir(connexion)

        # --------------------------------------------------------------------------------------------------------------
        # GESTION DES REQUETES
        # --------------------------------------------------------------------------------------------------------------

        # REQUÊTE: ENREGISTRER UN CLIENT (Retourne "0" si le pseudo existe déja, "1" si l'opération a réussi)

        if demande["type"] == "0":

            print("Demande d'enregistrement d'un client. Vérification de l'existence du client...")

            if CURSOR.execute("SELECT ID FROM USERS WHERE NOM=?", (demande["pseudo"],)).fetchone() is not None:

                print("Le client existe déja.")

                envoyer(connexion, {"reussi": "0"})

            else:

                print("Le client n'existe pas encore, création du client...")

                salt = hashlib.md5(demande["pseudo"].encode()).hexdigest()
                crypt = hashlib.sha1((salt+demande["password"]+"salt").encode()).hexdigest()
                CURSOR.execute("INSERT INTO USERS (PASSWORD, NOM) VALUES (?, ?)", (crypt, demande["pseudo"]))
                DATABASE.commit()
                envoyer(connexion, {"reussi": "1"})

                print("Client enregistré.")

        # REQUÊTE: VERIFIER UN CLIENT

        if demande["type"] == "1":

            print("Demande de vérification d'un client. Vérification de l'existence du client...")

            crypt = CURSOR.execute("SELECT PASSWORD FROM USERS WHERE NOM=?", (demande["pseudo"],)).fetchone()
            if crypt is None:
                envoyer(connexion, {"reussi": "0"})
            else:
                crypt = crypt[0]

            salt = hashlib.md5(demande["pseudo"].encode()).hexdigest()
            user_crypt = hashlib.sha1((salt+demande["password"]+"salt").encode()).hexdigest()
            if crypt == user_crypt:
                envoyer(connexion, {"reussi": "1"})
            else:
                envoyer(connexion, {"reussi": "0"})

            print("Vérification envoyée.")

        # REQUÊTE: ENREGISTRER UN NIVEAU

        if demande["type"] == "2":

            print("Demande d'enregistrement d'un niveau. Vérification du client et du nom du niveau...")

            crypt = CURSOR.execute("SELECT PASSWORD FROM USERS WHERE NOM=?", (demande["pseudo"],)).fetchone()[0]
            salt = hashlib.md5(demande["pseudo"].encode()).hexdigest()
            user_crypt = hashlib.sha1((salt+demande["password"]+"salt").encode()).hexdigest()
            assert crypt == user_crypt
            if CURSOR.execute("SELECT ID FROM LEVELS WHERE NOM=?", (demande["nom_niveau"],)).fetchone():
                envoyer(connexion, {"reussi": "0"})
                raise ValueError()

            print("Nom du niveau et client confirmés. Enregistrement dans la base de données...")

            query = "INSERT INTO LEVELS (NOM, NIVEAU) VALUES (?, ?)"
            CURSOR.execute(query, (demande["nom_niveau"], sql.Binary(demande["niveau"].encode("ISO-8859-1"))))
            DATABASE.commit()
            envoyer(connexion, {"reussi": "1"})

            print("Niveau enregistré.")

        # REQUÊTE: OBTENIR LISTE NIVEAUX

        elif demande["type"] == "3":

            print("Demande d'obtention de la liste des niveaux. Récupération puis envoie de la liste...")

            liste = CURSOR.execute("SELECT ID, NOM FROM LEVELS").fetchall()
            envoyer(connexion, {"liste_niveaux": "*".join([str(item[0])+","+item[1] for item in liste])})

            print("Liste envoyée.")

        # REQUÊTE: OBTENIR UN NIVEAU

        elif demande["type"] == "4":

            print("Demande d'obtention d'un niveau. Récupération et envoi du niveau...")

            niveau = CURSOR.execute("SELECT NIVEAU FROM LEVELS WHERE ID=?", (demande["id_niveau"],)).fetchone()[0]
            envoyer(connexion, {"niveau": niveau.decode("ISO-8859-1")})

            print("Niveau envoyé.")

        # REQUÊTE: SUPPRESSION D'UN NIVEAU

        elif demande["type"] == "5":

            print("Demande de suppression d'un niveau. Vérification du client...")

            crypt = CURSOR.execute("SELECT PASSWORD FROM USERS WHERE NOM=?", (demande["pseudo"],)).fetchone()[0]
            salt = hashlib.md5(demande["pseudo"].encode()).hexdigest()
            user_crypt = hashlib.sha1((salt+demande["password"]+"salt").encode()).hexdigest()
            assert crypt == user_crypt

            nom_niveau = CURSOR.execute("SELECT NOM FROM LEVELS WHERE ID=?", (demande["id_niveau"],)).fetchone()[0]
            assert nom_niveau.split(" - ")[1] == demande["pseudo"]

            print("Client vérifié. Suppression du niveau...")

            CURSOR.execute("DELETE FROM LEVELS WHERE ID=?", (demande["id_niveau"],))
            DATABASE.commit()
            envoyer(connexion, {"reussi": "1"})

            print("Niveau supprimé.")

    # Lorsqu'une erreur survient, déclenchée expres ou non, on déconnecte le client et on revient au début

    except:
        print("Une erreur est survenue.")

    # Déconnecter le client quoi qu'il arrive

    finally:
        print("Client déconnecté.")
        connexion.close()
