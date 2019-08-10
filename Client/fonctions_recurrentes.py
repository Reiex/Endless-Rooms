# -*- coding:utf_8 -*

import sfml as sf
from os import listdir, getcwd, mkdir
from sys import exit

# Liste qui indique si un bloc est traversable par toute entite mobile
TRAVERSABLE = [True, False, True, True, True, True, True, True, True, True,
               True, True, True, True, False, False, False, False, True]

# Valeur de la couleur noire pour le fond du jeu
VALEUR_NOIR = sf.Color(13, 13, 13)

# Caractères autorisés pour la création de session/niveaux
CARACTERES_AUTORISES = r"[A-Za-zÀ-ÿ0-9]"


# Classe a utiliser comme base pour toute entitée qui peut bouger en jeu

class EntiteMobile:

    def __init__(self, x_image=0, y_image=0, w_image=0, h_image=0, x_hitbox=0, y_hitbox=0, w_hitbox=0, h_hitbox=0):

        self.x_image = x_image
        self.y_image = y_image
        self.w_image = w_image
        self.h_image = h_image

        self.x_hitbox = x_hitbox
        self.y_hitbox = y_hitbox
        self.w_hitbox = w_hitbox
        self.h_hitbox = h_hitbox

        self.deplacement = {"x": 0, "y": 0}

    # Retourne True s'il y a collision

    def collision(self, rect_deux):

        if isinstance(rect_deux, tuple) or isinstance(rect_deux, list):
            if len(rect_deux) == 2:
                if self.x_hitbox <= rect_deux[0] <= self.x_hitbox+self.w_hitbox and \
                   self.y_hitbox <= rect_deux[1] <= self.y_hitbox+self.h_hitbox:
                    return True
                else:
                    return False
            elif len(rect_deux) == 4:
                if self.x_hitbox > rect_deux[0]+rect_deux[2] or \
                   rect_deux[0] > self.x_hitbox+self.w_hitbox or \
                   self.y_hitbox >= rect_deux[1]+rect_deux[3] or \
                   rect_deux[1] >= self.y_hitbox+self.h_hitbox:
                    return False
                else:
                    return True
            else:
                raise ValueError(rect_deux, " ne possede pas le nombre adéquat d'argument pour verifier une collision")
        elif "x_hitbox" in dir(rect_deux) and "y_hitbox" in dir(rect_deux):
            if "w_hitbox" in dir(rect_deux) and "h_hitbox" in dir(rect_deux):
                if self.x_hitbox > rect_deux.x_hitbox+rect_deux.w_hitbox or \
                   rect_deux.x_hitbox > self.x_hitbox+self.w_hitbox or \
                   self.y_hitbox >= rect_deux.y_hitbox+rect_deux.h_hitbox or \
                   rect_deux.y_hitbox >= self.y_hitbox+self.h_hitbox:
                    return False
                else:
                    return True
            else:
                if self.x_hitbox <= rect_deux.x_hitbox <= self.x_hitbox+self.w_hitbox and \
                   self.y_hitbox <= rect_deux.y_hitbox <= self.y_hitbox+self.h_hitbox:
                    return True
                else:
                    return False
        else:
            raise ValueError(rect_deux, " n'est pas un objet valide pour verifier une collision.")

    # Deplace l'entite et retourne True s'il y a collision lors du deplacement

    def deplacer(self, etage):

        collision = False

        # Déplacer sur l'axe horizontale

        if self.deplacement["x"] != 0:

            # Ajouter le déplacement puis calculer les blocs qui sont susceptibles d'être en collision avec l'entite

            self.x_image += self.deplacement["x"]
            self.x_hitbox += self.deplacement["x"]

            bloc_zero = (self.x_hitbox//64, self.y_hitbox//64)
            blocs_proches = list()
            for i in range(self.w_hitbox//64+2):
                for j in range(self.h_hitbox//64+2):
                    if 0 <= bloc_zero[0]+i < etage.blocs.shape[0] and 0 <= bloc_zero[1]+j < etage.blocs.shape[1]:
                        blocs_proches.append((bloc_zero[0]+i, bloc_zero[1]+j))

            # Pour chacun de ces blocs, verifier le type, s'il y a collision, et faire reculer l'entite si besoin

            for bloc in blocs_proches:

                while not TRAVERSABLE[etage.blocs[bloc]] and self.collision((bloc[0]*64, bloc[1]*64, 64, 64)):

                    collision = True
                    if self.deplacement["x"] > 0:
                        self.x_image -= 1
                        self.x_hitbox -= 1
                    else:
                        self.x_image += 1
                        self.x_hitbox += 1

                    if self.x_hitbox//64 != blocs_proches[0][0]:
                        bloc_zero = (self.x_hitbox//64, self.y_hitbox//64)
                        blocs_proches = list()
                        for i in range(self.w_hitbox//64+2):
                            for j in range(self.h_hitbox//64+2):
                                if 0 <= bloc_zero[0]+i < etage.blocs.shape[0] and 0 <= bloc_zero[1]+j < etage.blocs.shape[1]:
                                    blocs_proches.append((bloc_zero[0]+i, bloc_zero[1]+j))

        if self.deplacement["y"] != 0:

            # Ajouter le déplacement puis calculer les blocs qui sont susceptibles d'être en collision avec l'entite

            self.y_image += self.deplacement["y"]
            self.y_hitbox += self.deplacement["y"]

            bloc_zero = (self.x_hitbox//64, self.y_hitbox//64)
            blocs_proches = list()
            for i in range(self.w_hitbox//64+2):
                for j in range(self.h_hitbox//64+2):
                    if 0 <= bloc_zero[0]+i < etage.blocs.shape[0] and 0 <= bloc_zero[1]+j < etage.blocs.shape[1]:
                        blocs_proches.append((bloc_zero[0]+i, bloc_zero[1]+j))

            # Pour chacun de ces blocs, verifier le type, s'il y a collision, et faire reculer l'entite si besoin

            for bloc in blocs_proches:

                while not TRAVERSABLE[etage.blocs[bloc]] and self.collision((bloc[0]*64, bloc[1]*64, 64, 64)):

                    collision = True
                    if self.deplacement["y"] > 0:
                        self.y_image -= 1
                        self.y_hitbox -= 1
                    else:
                        self.y_image += 1
                        self.y_hitbox += 1

                    if self.y_hitbox//64 != blocs_proches[0][1]:
                        bloc_zero = (self.x_hitbox//64, self.y_hitbox//64)
                        blocs_proches = list()
                        for i in range(self.w_hitbox//64+2):
                            for j in range(self.h_hitbox//64+2):
                                if 0 <= bloc_zero[0]+i < etage.blocs.shape[0] and 0 <= bloc_zero[1]+j < etage.blocs.shape[1]:
                                    blocs_proches.append((bloc_zero[0]+i, bloc_zero[1]+j))

        return collision


# Fonction limitant les fps

def gerer_fps(temps_actuel):

    print(temps_actuel.elapsed_time.milliseconds)
    if temps_actuel.elapsed_time.milliseconds < 30:
        sf.sleep(sf.milliseconds(30-temps_actuel.elapsed_time.milliseconds))

    temps_actuel.restart()


# Fonction permettant l'obtention de la liste des sessions présentes dans le dossier save

def obtenir_liste_noms_sessions():

    if "save" in listdir(getcwd()):
        liste_fichiers = listdir(getcwd()+"/save")
        liste_noms = list()
        for fichier in liste_fichiers:
            liste_noms.append(fichier.replace(".elr", ""))
        return liste_noms
    else:
        mkdir(getcwd()+"/save")
        return list()


# Fonction permettant l'obtention de la liste des niveaux présents dans le dossier edit

def obtenir_liste_noms_etages():

    if "edit" in listdir(getcwd()):
        liste_fichiers = listdir(getcwd()+"/edit")
        liste_noms = list()
        for fichier in liste_fichiers:
            liste_noms.append(fichier.replace(".png", ""))
        return liste_noms
    else:
        mkdir(getcwd()+"/edit")
        return list()


# Fonction pour sauvegarder et quitter le jeu

def save_and_quit(arg, session):

    session.sauvegarder()
    exit(arg)


# Explore une variable et renvoie True si les variables ne sont que des types de python

def explorer(item):

    objet_simple = True
    types_simples_python = [int, float, str, bool]
    types_complexes_python = [list, tuple, dict]

    if isinstance(item, dict):
        for key in item:
            if type(item[key]) in types_complexes_python:
                objet_simple = explorer(item[key])
            elif type(item[key]) not in types_simples_python:
                return False
    elif isinstance(item, list) or isinstance(item, tuple):
        for var in item:
            if type(var) in types_complexes_python:
                objet_simple = explorer(var)
            elif type(var) not in types_simples_python:
                return False
    elif type(item) in types_simples_python:
        return True
    else:
        return False

    return objet_simple