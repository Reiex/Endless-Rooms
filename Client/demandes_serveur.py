# -*- coding:utf-8 -*

from etage import *
import socket

ADRESSE_IP_SERVEUR = "51.254.100.173"
PORT = 25099
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


# Fonction permettant d'inscrire un nouveau compte dans la base de données

@ecran_de_chargement("Connexion")
def inscription_bdd(pseudo, password, **kwargs):

    try:

        # Connection au serveur
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.settimeout(1.0)
        connexion.connect((ADRESSE_IP_SERVEUR, PORT))

        # Envoi de la demande
        envoyer(connexion, {"type": "0", "pseudo": pseudo, "password": password})

        # Réception de la réponse
        resultat = recevoir(connexion)

        connexion.close()
        return bool(int(resultat["reussi"]))

    except socket.error:
        return "Error"


# Fonction permettant de verifier si le pseudo et le mot de passe concordent avec un compte de la base de données

@ecran_de_chargement("Connexion")
def verification_connexion_bdd(pseudo, password, **kwargs):

    try:

        # Connection au serveur
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.settimeout(1.0)
        connexion.connect((ADRESSE_IP_SERVEUR, PORT))

        # Envoi de la demande
        envoyer(connexion, {"type": "1", "pseudo": pseudo, "password": password})

        # Réception de la réponse
        resultat = recevoir(connexion)

        connexion.close()
        return bool(int(resultat["reussi"]))

    except socket.error:
        return "Error"


# Fonction qui enregistre un niveau dans la base de données en récupirant le png dans edit/nom.png

@ecran_de_chargement("Connexion")
def enregistrer_niveau_bdd(pseudo, password, nom_fichier, **kwargs):

    try:

        # Connection au serveur
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.settimeout(1.0)
        connexion.connect((ADRESSE_IP_SERVEUR, PORT))

        # Envoi de la demande
        with open("edit/"+nom_fichier, "rb") as image_niveau:
            niveau = image_niveau.read()
        message = {"type": "2", "nom_niveau": nom_fichier[:-4]+" - "+pseudo,
                   "password": password, "niveau": niveau.decode("ISO-8859-1"), "pseudo": pseudo}
        envoyer(connexion, message)

        # Réception de la réponse
        resultat = recevoir(connexion)

        connexion.close()
        return bool(int(resultat["reussi"]))

    except socket.error:
        return "Error"


# Fonction qui retourne une liste contenant l'ID et le nom de chaque niveau en ligne

@ecran_de_chargement("Connexion")
def obtenir_liste_niveaux_bdd(**kwargs):

    try:

        # Connection au serveur
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.settimeout(1.0)
        connexion.connect((ADRESSE_IP_SERVEUR, PORT))

        # Envoi de la demande
        envoyer(connexion, {"type": "3"})

        # Réception de la réponse
        resultat = recevoir(connexion)

        connexion.close()
        liste = [niveau.split(",") for niveau in resultat["liste_niveaux"].split("*")]
        return [niveau for niveau in liste if niveau != [""]]

    except socket.error:
        return "Error"


# Fonction qui enregistre dans un fichier sous edit/nom.png le niveau qui a la bonne ID dans la base de données

@ecran_de_chargement("Connexion")
def telecharger_niveau_bdd(id_niveau, nom, **kwargs):

    try:

        # Connection au serveur
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.settimeout(1.0)
        connexion.connect((ADRESSE_IP_SERVEUR, PORT))

        # Envoi de la demande
        envoyer(connexion, {"type": "4", "id_niveau": id_niveau})

        # Réception de la réponse
        resultat = recevoir(connexion)

        connexion.close()

        with open(nom+".png", "wb") as image_niveau:
            image_niveau.write(resultat["niveau"].encode("ISO-8859-1"))

    except socket.error:
        return "Error"


# Fonction qui supprime un niveau de la base de données

@ecran_de_chargement("Connexion")
def supprimer_niveau_bdd(id_niveau, pseudo, password, **kwargs):

    try:

        # Connection au serveur
        connexion = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connexion.settimeout(1.0)
        connexion.connect((ADRESSE_IP_SERVEUR, PORT))

        # Envoi de la demande
        envoyer(connexion, {"type": "5", "pseudo": pseudo, "password": password, "id_niveau": id_niveau})

        # Réception de la réponse
        resultat = recevoir(connexion)

        connexion.close()
        return bool(int(resultat["reussi"]))

    except socket.error:
        return "Error"
