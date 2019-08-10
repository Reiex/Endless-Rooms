# -*- coding:utf_8 -*

from joueur import *
from math import fabs, degrees, acos
import numpy as np
from os import remove

tileset_image = sf.Image.from_file("images/tileset.png")
tileset_anime_image = sf.Image.from_file("images/tileset_anime.png")
interface_image = sf.Image.from_file("images/interface.png")
attaques_image = sf.Image.from_file("images/attaques.png")
tileset_image.create_mask_from_color(sf.Color(255, 255, 255))
tileset_anime_image.create_mask_from_color(sf.Color(255, 255, 255))
interface_image.create_mask_from_color(sf.Color(255, 255, 255))
attaques_image.create_mask_from_color(sf.Color(255, 255, 255))

TILESET = sf.Texture.from_image(tileset_image)
TILESET_ANIME = sf.Texture.from_image(tileset_anime_image)
INTERFACE = sf.Texture.from_image(INTERFACE_IMAGE)
ATTAQUES = sf.Texture.from_image(attaques_image)
BACKGROUND = sf.Texture.from_file("images/background.png")

# Obtenir la taille maximale des textures, et s'assurer que c'est un multiple de 64
TEXTURE_MAX = (sf.Texture.get_maximum_size()//2)//64*64

# Dictionnaire qui associe a chaque couleur de pixel son bloc
BLOCS_COULEUR = {"255,255,255": 0, "50,50,50": 0, "0,0,0": 1, "100,100,100": 2, "101,101,101": 3,
                 "150,150,150": 4, "151,151,151": 5, "152,152,152": 6, "153,153,153": 7, "255,0,0": 8,
                 "102,102,102": 9, "103,103,103": 10, "200,200,200": 11, "255,50,50": 12, "225,225,225": 13,
                 "175,175,175": 14, "176,176,176": 15, "177,177,177": 16, "178,178,178": 17, "125,125,125": 18}

# Liste qui associe a chaque bloc les degats qu'il inflige ( mettre une valeur negative si c'est un soin )
DEGATS = [0, 0, 0, 0, 1, 1, 1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Liste des blocs faisant partie de portes, la première liste pour le bloc du bas, la seconde pour le bloc du haut
LISTE_PORTES = [[2, 9], [3, 10]]

# Shader qui permet d'afficher un effet d'ombres
SHADER_OMBRE = sf.Shader.from_file(None, "shader/ombre.frag")


class Etage:

    def __init__(self, level, mode_tutoriel=False):

        self.level = level
        self.mode_tutoriel = mode_tutoriel
        self.taille = [0, 0]
        self.decalage = [0, 0]
        self.blocs = np.array([], np.uint16)
        self.fond = list()
        self.joueur = Joueur()
        self.monstres = list()
        self.blocs_importants = {"sprites_animes": list(), "portes": list(), "brasiers": list(), "mobiles": list(),
                                 "fenetres": list(), "pieges": list()}

        self.tempo = int()
        self.tempo_lent = int()
        self.temps_niveau = int()

        self.attaques = list()
        self.fenetre = Fenetre(None)
        self.refresh_list = list()

    # Methode qui sert à charger un niveau

    @ecran_de_chargement("Chargement")
    def charger_etage(self, **kwargs):

        self.fenetre = None

        # Charger le plan du niveau

        if isinstance(self.level, int):
            image_niveau = sf.Image.from_file("levels/"+("tuto" if self.mode_tutoriel else "level")+str(self.level)+".png")
        else:
            if self.level[-4:] != ".png":
                image_niveau = sf.Image.from_file("edit/"+self.level+".png")
            else:
                image_niveau = sf.Image.from_file(self.level)

        # Obtenir la taille de la map et créer des textures modifiables qui serviront de fond a la salle

        self.taille = [image_niveau.width, image_niveau.height]
        self.fond = list()
        for y in range((self.taille[1]*64)//TEXTURE_MAX+1):
            self.fond.append(list())
            for x in range((self.taille[0]*64//TEXTURE_MAX+1)):
                self.fond[y].append(sf.RenderTexture(TEXTURE_MAX, TEXTURE_MAX))
        self.blocs.resize(self.taille)

        # Obtenir chaque bloc et le placer dans self.blocs

        for y in range(self.taille[1]):
            for x in range(self.taille[0]):

                # Blocs normaux

                chaine = "{r},{g},{b}".format(r=image_niveau[x, y].r, g=image_niveau[x, y].g, b=image_niveau[x, y].b)

                if chaine in BLOCS_COULEUR.keys():
                    self.blocs[x, y] = BLOCS_COULEUR[chaine]

                    # Spawn
                    if image_niveau[x, y] == sf.Color(50, 50, 50):
                        self.joueur.x_image, self.joueur.y_image = 64*x, 64*y
                        self.joueur.x_hitbox, self.joueur.y_hitbox = self.joueur.x_image+11, self.joueur.y_image+6

                    # Blocs animes
                    elif image_niveau[x, y] == sf.Color(255, 0, 0):
                        self.blocs_importants["sprites_animes"].append((x, y))

                    # Portes
                    elif self.blocs[x, y] in LISTE_PORTES[0] or self.blocs[x, y] in LISTE_PORTES[1]:
                        self.blocs_importants["portes"].append((x, y))

                    # Brasiers
                    elif image_niveau[x, y] == sf.Color(200, 200, 200):
                        self.blocs_importants["brasiers"].append((x, y))
                    elif image_niveau[x, y] == sf.Color(255, 50, 50):
                        self.blocs_importants["sprites_animes"].append((x, y))
                        self.blocs_importants["brasiers"].append((x, y))

                    # Pieges
                    elif image_niveau[x, y] == sf.Color(175, 175, 175) or \
                         image_niveau[x, y] == sf.Color(176, 176, 176) or \
                         image_niveau[x, y] == sf.Color(177, 177, 177) or \
                         image_niveau[x, y] == sf.Color(178, 178, 178):
                        self.blocs_importants["pieges"].append((x, y))

                # Monstres

                elif image_niveau[x, y].r == image_niveau[x, y].g == 255 and image_niveau[x, y].b != 255:
                    self.monstres.append(Monstre(image_niveau[x, y].b, x*64, y*64, 64, 64, x*64, y*64,
                                                 DATA_MONSTRES[image_niveau[x, y].b]["taille-px"][0],
                                                 DATA_MONSTRES[image_niveau[x, y].b]["taille-px"][1]))

                # Fenetres

                elif image_niveau[x, y].r == image_niveau[x, y].b == 255 and image_niveau[x, y].g != 255:
                    self.blocs[x, y] = 0
                    self.blocs_importants["fenetres"].append((x, y, image_niveau[x, y].g))

        # Dessiner chaque bloc

        for y in range(self.taille[1]):
            for x in range(self.taille[0]):

                # Verifier si le bloc est un sprite animé

                if (x, y) not in self.blocs_importants["sprites_animes"]:
                    sprite = sf.Sprite(TILESET, ((self.blocs[x, y] % 10)*64, (self.blocs[x, y]//10)*64, 64, 64))
                else:
                    sprite = sf.Sprite(TILESET, (0, 0, 64, 64))

                # Dessiner le sprite

                self.parametrer_shader_ombre(x, y)
                sprite.position = ((x*64) % TEXTURE_MAX, (y*64) % TEXTURE_MAX)
                self.fond[(y*64)//TEXTURE_MAX][(x*64)//TEXTURE_MAX].draw(sprite, sf.RenderStates(shader=SHADER_OMBRE))

        # Mettre a jour le fond de la salle

        for item in self.fond:
            for chunk in item:
                chunk.display()

        # Effacer l'image de la map si c'était un niveau en ligne

        if isinstance(self.level, str):
            if self.level[-4:] == ".png":
                remove(getcwd()+"/"+self.level)

    # Méthode chargée d'envoyer les bon paramètre au shader ombre pour chaque bloc

    def parametrer_shader_ombre(self, x, y):

        # Blocs adjacents

        if y > 0:
            SHADER_OMBRE.set_2float_parameter("bloc_haut", int(TRAVERSABLE[self.blocs[x, y-1]]), self.blocs[x, y-1])
        else:
            SHADER_OMBRE.set_2float_parameter("bloc_haut", False, 1)

        if y < self.taille[1]-1:
            SHADER_OMBRE.set_2float_parameter("bloc_bas", int(TRAVERSABLE[self.blocs[x, y+1]]), self.blocs[x, y+1])
        else:
            SHADER_OMBRE.set_2float_parameter("bloc_bas", False, 1)

        if x > 0:
            SHADER_OMBRE.set_2float_parameter("bloc_gauche", int(TRAVERSABLE[self.blocs[x-1, y]]), self.blocs[x-1, y])
        else:
            SHADER_OMBRE.set_2float_parameter("bloc_gauche", False, 1)

        if x < self.taille[0]-1:
            SHADER_OMBRE.set_2float_parameter("bloc_droite", int(TRAVERSABLE[self.blocs[x+1, y]]), self.blocs[x+1, y])
        else:
            SHADER_OMBRE.set_2float_parameter("bloc_droite", False, 1)

        # Blocs diagonnaux

        if y > 0 and x > 0:
            SHADER_OMBRE.set_2float_parameter("bloc_haut_gauche",
                                              int(TRAVERSABLE[self.blocs[x-1, y-1]]), self.blocs[x-1, y-1])
        else:
            SHADER_OMBRE.set_2float_parameter("bloc_haut_gauche", False, 1)

        if y > 0 and x < self.taille[0]-1:
            SHADER_OMBRE.set_2float_parameter("bloc_haut_droite",
                                              int(TRAVERSABLE[self.blocs[x+1, y-1]]), self.blocs[x+1, y-1])
        else:
            SHADER_OMBRE.set_2float_parameter("bloc_haut_droite", False, 1)

        if y < self.taille[1]-1 and x > 0:
            SHADER_OMBRE.set_2float_parameter("bloc_bas_gauche",
                                              int(TRAVERSABLE[self.blocs[x-1, y+1]]), self.blocs[x-1, y+1])
        else:
            SHADER_OMBRE.set_2float_parameter("bloc_bas_gauche", False, 1)

        if y < self.taille[1]-1 and x < self.taille[0]-1:
            SHADER_OMBRE.set_2float_parameter("bloc_bas_droite",
                                              int(TRAVERSABLE[self.blocs[x+1, y+1]]), self.blocs[x+1, y+1])
        else:
            SHADER_OMBRE.set_2float_parameter("bloc_bas_droite", False, 1)

        SHADER_OMBRE.set_2float_parameter("pos_bloc", (x*64) % TEXTURE_MAX, (y*64) % TEXTURE_MAX)
        SHADER_OMBRE.set_2float_parameter("bloc", int(TRAVERSABLE[self.blocs[x, y]]), self.blocs[x, y])
        SHADER_OMBRE.set_1float_parameter("taille_texture", TEXTURE_MAX)

    # Méthode chargée de créer l'image à afficher à chaque tour en fonction de la refresh_list

    def afficher_image_jeu(self, window, resolution):

        # Obtenir les coordonnees du point en haut a gauche de la fenetre par rapport aux coordonnees de la salle

        self.decalage = [self.joueur.x_image-(resolution["w"]-self.joueur.w_image)//2,
                         self.joueur.y_image-(resolution["h"]-self.joueur.h_image)//2]

        if self.taille[0]*64 < resolution["w"]:
            self.decalage[0] = -(resolution["w"]-self.taille[0]*65)//2
        elif self.decalage[0] < 0:
            self.decalage[0] = 0
        elif self.decalage[0]+resolution["w"] > self.taille[0]*64:
            self.decalage[0] = self.taille[0]*64-resolution["w"]

        if self.taille[1]*64 < resolution["h"]:
            self.decalage[1] = -(resolution["h"]-self.taille[1]*64)//2
        elif self.decalage[1] < 0:
            self.decalage[1] = 0
        elif self.decalage[1]+resolution["h"] > self.taille[1]*64:
            self.decalage[1] = self.taille[1]*64-resolution["h"]

        # Netoyer l'ecran

        window.clear(VALEUR_NOIR)

        # Dessiner le background

        decalage_background = [(self.decalage[0] % 1024)//2, (self.decalage[1] % 1024)//2]
        for y in range(resolution["h"]//512+2):
            for x in range(resolution["w"]//512+2):
                if 0 < self.decalage[0]+x*512-decalage_background[0] < self.taille[0]*64-512 and \
                   0 < self.decalage[1]+y*512-decalage_background[1] < self.taille[1]*64-512:
                    sprite = sf.Sprite(BACKGROUND)
                    sprite.position = (x*512-decalage_background[0], y*512-decalage_background[1])
                else:
                    fenetre = [0, 0, 512, 512]

                    if self.decalage[0]+x*512-decalage_background[0] < 0:
                        fenetre[2] -= -(self.decalage[0]+x*512-decalage_background[0])
                        fenetre[0] = -(self.decalage[0]+x*512-decalage_background[0])
                    if self.decalage[0]+x*512+512-decalage_background[0] > self.taille[0]*64:
                        fenetre[2] -= self.decalage[0]+x*512+512-decalage_background[0]-self.taille[0]*64

                    if self.decalage[1]+y*512-decalage_background[1] < 0:
                        fenetre[3] -= -(self.decalage[1]+y*512-decalage_background[1])
                        fenetre[1] = -(self.decalage[1]+y*512-decalage_background[1])
                    if self.decalage[1]+y*512+512-decalage_background[1] > self.taille[1]*64:
                        fenetre[3] -= self.decalage[1]+y*512+512-decalage_background[1]-self.taille[1]*64

                    if fenetre[2] < 0 or fenetre[3] < 0:
                        continue

                    sprite = sf.Sprite(BACKGROUND, fenetre)
                    sprite.position = (x*512-decalage_background[0]+fenetre[0], y*512-decalage_background[1]+fenetre[1])

                window.draw(sprite)

        # Dessiner le décor

        fenetre = {"min-x": self.decalage[0]//TEXTURE_MAX-1,
                   "min-y": self.decalage[1]//TEXTURE_MAX-1,
                   "max-x": (self.decalage[0]+resolution["w"])//TEXTURE_MAX+1,
                   "max-y": (self.decalage[1]+resolution["h"])//TEXTURE_MAX+1}

        for y, item in enumerate(self.fond):
            for x, chunk in enumerate(item):
                if fenetre["min-x"] <= x <= fenetre["max-x"] and fenetre["min-y"] <= y <= fenetre["max-y"]:
                    sprite = sf.Sprite(chunk.texture)
                    sprite.position = (x*TEXTURE_MAX-self.decalage[0], y*TEXTURE_MAX-self.decalage[1])
                    window.draw(sprite)

        # Dessiner les sprites animés

        self.animer_sprites(window, resolution)

        # Dessiner chaque élément mobile (joueur, attaques, monstres...)

        self.refresh_list = sorted(self.refresh_list, key=lambda image: image[1])
        for element in self.refresh_list:
            element[0].position = (element[0].position.x-self.decalage[0], element[0].position.y-self.decalage[1])
            window.draw(element[0])
        self.refresh_list = list()

    # Méthode qui déplace le joueur

    def deplacer_joueur(self, raccourcis):

        # CALCULER LE DEPLACEMENT DU JOUEUR

        # Obtenir le déplacement sur l'axe horizontal

        if sf.Keyboard.is_key_pressed(raccourcis["droite"][0]) and \
           not sf.Keyboard.is_key_pressed(raccourcis["gauche"][0]):
            self.joueur.deplacement["x"] = self.joueur.vitesse
        elif sf.Keyboard.is_key_pressed(raccourcis["gauche"][0]) and \
                not sf.Keyboard.is_key_pressed(raccourcis["droite"][0]):
            self.joueur.deplacement["x"] = -self.joueur.vitesse
        else:
            self.joueur.deplacement["x"] = 0

        # Obtenir le déplacement sur l'axe vertical

        if TRAVERSABLE[self.blocs[self.joueur.x_hitbox//64, (self.joueur.y_hitbox+self.joueur.h_hitbox+1)//64]] and \
           TRAVERSABLE[self.blocs[(self.joueur.x_hitbox+self.joueur.w_hitbox)//64, (self.joueur.y_hitbox+self.joueur.h_hitbox+1)//64]]:
            self.joueur.deplacement["y"] += 2
            if self.joueur.deplacement["y"] == 0 or \
               not TRAVERSABLE[self.blocs[self.joueur.x_hitbox//64, (self.joueur.y_hitbox-1)//64]] or \
               not TRAVERSABLE[self.blocs[(self.joueur.x_hitbox+self.joueur.w_hitbox)//64, (self.joueur.y_hitbox-1)//64]]:
                self.joueur.deplacement["y"] = 1
        else:
            if sf.Keyboard.is_key_pressed(raccourcis["saut"][0]):
                self.joueur.deplacement["y"] = -30
            elif self.joueur.deplacement["y"] >= 0:
                self.joueur.deplacement["y"] = 0

        if self.joueur.deplacement["y"] > 48:
            self.joueur.deplacement["y"] = 48
        if self.joueur.deplacement["y"] < -48:
            self.joueur.deplacement["y"] = -48

        # Modifier le déplacement sur l'axe vertical si le joueur est sur une echelle

        if sf.Keyboard.is_key_pressed(raccourcis["saut"][0]):
            if self.blocs[self.joueur.x_hitbox//64, (self.joueur.y_hitbox+self.joueur.h_hitbox)//64] == 13 or \
               self.blocs[(self.joueur.x_hitbox+self.joueur.w_hitbox)//64, (self.joueur.y_hitbox+self.joueur.h_hitbox)//64] == 13:
                self.joueur.deplacement["y"] = -15

        # DEPLACER LE JOUEUR

        self.joueur.deplacer(self)

        # GERER LES EFFETS DES BLOCS EN COLLISION AVEC LE JOUEUR

        blocs_proches = [(self.joueur.x_hitbox//64, self.joueur.y_hitbox//64)]
        blocs_proches += [(blocs_proches[0][0]+1, blocs_proches[0][1]),
                          (blocs_proches[0][0], blocs_proches[0][1]+1),
                          (blocs_proches[0][0]+1, blocs_proches[0][1]+1),
                          (blocs_proches[0][0], blocs_proches[0][1]+2),
                          (blocs_proches[0][0]+1, blocs_proches[0][1]+2)]

        # Blocs qui infligent des dégats

        for bloc in blocs_proches:
            if DEGATS[self.blocs[bloc]] != 0:
                if self.joueur.collision((bloc[0]*64, bloc[1]*64, 64, 64)):
                    self.joueur.vie -= DEGATS[self.blocs[bloc]]

        # Bumpers

        for bloc in blocs_proches:
            if self.blocs[bloc] == 18:
                if self.joueur.collision((bloc[0]*64, bloc[1]*64, 64, 64)):
                    self.joueur.deplacement["y"] = -45

        # AFFICHER LE JOUEUR

        if self.joueur.deplacement["x"] < 0:
            direction = "gauche"
        else:
            direction = "droite"

        if self.joueur.deplacement["y"] != 0:
            evenement = "saut"
        elif self.joueur.deplacement["x"] != 0:
            evenement = "course"
        else:
            evenement = "arret"

        if sf.Mouse.is_button_pressed(sf.Mouse.LEFT):
            evenement += "-attaque"

        if "course" in evenement:

            self.joueur.images[direction][evenement][self.tempo//6].position = (self.joueur.x_image, self.joueur.y_image)
            if self.joueur.invincible:
                self.joueur.images[direction][evenement][self.tempo//6].color = sf.Color(255, 255, 255, 127)
            else:
                if self.joueur.images[direction][evenement][self.tempo//6].color == sf.Color(255, 255, 255, 127):
                    self.joueur.images[direction][evenement][self.tempo//6].color = sf.Color(255, 255, 255, 255)
            self.refresh_list.append([self.joueur.images[direction][evenement][self.tempo//6], 10])

        else:

            self.joueur.images[direction][evenement].position = (self.joueur.x_image, self.joueur.y_image)
            if self.joueur.invincible:
                self.joueur.images[direction][evenement].color = sf.Color(255, 255, 255, 127)
            else:
                if self.joueur.images[direction][evenement].color == sf.Color(255, 255, 255, 127):
                    self.joueur.images[direction][evenement].color = sf.Color(255, 255, 255, 255)
            self.refresh_list.append([self.joueur.images[direction][evenement], 10])

    # Méthode qui s'occupe d'afficher l'interface

    def afficher_interface(self, window, resolution):

        # Afficher les points de vie

        vie_a_afficher = self.joueur.vie
        for i in range(self.joueur.vie_maximum//2):
            if vie_a_afficher >= 2:
                sprite = sf.Sprite(INTERFACE, (0, 0, 48, 48))
                vie_a_afficher -= 2
            elif vie_a_afficher == 1:
                sprite = sf.Sprite(INTERFACE, (48, 0, 48, 48))
                vie_a_afficher -= 1
            else:
                sprite = sf.Sprite(INTERFACE, (96, 0, 48, 48))
            sprite.position = (window.view.center.x+resolution["w"]//2-(self.joueur.vie_maximum//2)*64+i*64,
                               window.view.center.y-resolution["h"]//2)
            window.draw(sprite)

        # Afficher le nombre de brasiers restant

        brasiers_affiches = 0
        sprite = sf.Sprite(INTERFACE, (0, 48, 48, 48))
        for bloc in self.blocs_importants["brasiers"]:
            if self.blocs[bloc] == 12:
                sprite.position = (window.view.center.x-resolution["w"]//2+brasiers_affiches*48+16,
                                   window.view.center.y+resolution["h"]//2-64)
                window.draw(sprite)
                brasiers_affiches += 1

        sprite = sf.Sprite(INTERFACE, (48, 48, 48, 48))
        for bloc in self.blocs_importants["brasiers"]:
            if self.blocs[bloc] == 11:
                sprite.position = (window.view.center.x-resolution["w"]//2+brasiers_affiches*48+16,
                                   window.view.center.y+resolution["h"]//2-64)
                window.draw(sprite)
                brasiers_affiches += 1

    # Méthode qui créer les attaques du joueur en fonction des evenements

    def creer_attaques_joueur(self, window, resolution):

        # CREER LES ATTAQUES DE BASE

        if sf.Mouse.is_button_pressed(sf.Mouse.LEFT):

            position_souris = sf.Mouse.get_position(window)

            if self.joueur.derniere_attaque.elapsed_time.seconds > self.joueur.temps_entre_attaques and \
               0 <= position_souris.x <= resolution["w"] and 0 <= position_souris.y <= resolution["h"]:

                attaque = Attaque(0, w_hitbox=10, h_hitbox=10)

                # Obtenir la position ciblée et le vecteur qu'il forme avec la position du joueur

                cible_x = position_souris.x+self.decalage[0]
                cible_y = position_souris.y+self.decalage[1]
                difference_x = fabs(cible_x-self.joueur.x_image-18)
                difference_y = fabs(cible_y-self.joueur.y_image-50)

                # Calculer le vecteur final de l'attaque

                attaque.deplacement["x"] = int((difference_x/(difference_x+difference_y))*26)
                attaque.deplacement["y"] = int((difference_y/(difference_x+difference_y))*26)
                if cible_x < self.joueur.x_image+18:
                    attaque.deplacement["x"] = -attaque.deplacement["x"]
                if cible_y < self.joueur.y_image+50:
                    attaque.deplacement["y"] = -attaque.deplacement["y"]

                # Calculer les coordonnees et obtenir les images de l'attaque, puis ajouter l'attaque a la liste

                attaque.x_hitbox = self.joueur.x_image+22
                attaque.y_hitbox = self.joueur.y_image+59
                attaque.images = {"projectile": sf.Sprite(ATTAQUES, (0, 0, 28, 40)),
                                  "impacte": sf.Sprite(ATTAQUES, (0, 40, 40, 40))}
                attaque.images["projectile"].origin = (14, 20)

                self.attaques.append(attaque)
                self.joueur.derniere_attaque.restart()

    # Méthode qui déplace toutes les attaques en cour

    def deplacer_attaque(self):

        for attaque in self.attaques:

            if not attaque.detruit:

                # ATTAQUES DE BASE

                if attaque.type == 0:

                    if self.tempo % 4 == 0 and attaque.deplacement["y"] < 60:
                        attaque.deplacement["y"] += 1
                    if attaque.deplacement["x"] == 0 and attaque.deplacement["y"] == 0:
                        attaque.deplacement["y"] = 1

                    # Créer l'image du projectile et calculer les coordonnees

                    attaque.images["projectile"].rotation = 180-degrees(acos((20*attaque.deplacement["y"])/(20*(attaque.deplacement["x"]**2+attaque.deplacement["y"]**2)**(1/2))))
                    if attaque.deplacement["x"] < 0:
                        attaque.images["projectile"].rotation = 360-attaque.images["projectile"].rotation

                    attaque.w_image = attaque.images["projectile"].global_bounds.width
                    attaque.h_image = attaque.images["projectile"].global_bounds.height
                    attaque.x_image = attaque.x_hitbox+attaque.w_hitbox//2-attaque.w_image//2
                    attaque.y_image = attaque.y_hitbox+attaque.h_hitbox//2-attaque.h_image//2

                    # Deplacer le projectile

                    attaque.detruit = attaque.deplacer(self)

                    # Verifier si le projectile n'allume pas un brasier

                    for bloc in self.blocs_importants["brasiers"]:
                        if attaque.collision((bloc[0]*64, bloc[1]*64, 64, 64)):
                            self.blocs[bloc] = 12
                            if bloc not in self.blocs_importants["sprites_animes"]:
                                self.blocs_importants["sprites_animes"].append(bloc)

                    # Verifier si le projectile ne touche pas un ennemi

                    for monstre in self.monstres:
                        if monstre.actif:
                            if attaque.collision(monstre):
                                monstre.vie -= self.joueur.degats
                                attaque.detruit = True
                                break

                    # Afficher le projectile

                    attaque.images["projectile"].position = (attaque.x_image+attaque.w_image//2,
                                                             attaque.y_image+attaque.h_image//2)
                    self.refresh_list.append([attaque.images["projectile"], 8])

                # FLECHES DU LANCE-FLECHES

                if attaque.type == 1:

                    attaque.detruit = attaque.deplacer(self)

                    # Verifier si la fleche touche un ennemi

                    for monstre in self.monstres:
                        if monstre.actif:
                            if attaque.collision(monstre):
                                monstre.vie -= 1
                                attaque.detruit = True
                                break

                    # Verifier si la fleche touche le joueur

                    if attaque.collision(self.joueur):
                        self.joueur.vie -= 1
                        attaque.detruit = True

                    # Afficher le projectile

                    attaque.images["projectile"].position = (attaque.x_image+attaque.w_image//2,
                                                             attaque.y_image+attaque.h_image//2)
                    self.refresh_list.append([attaque.images["projectile"], 8])

    # Méthode qui détruit l'attaque

    def detruire_attaque(self):
        i = 0
        while i < len(self.attaques):
            if self.attaques[i].detruit:

                if self.attaques[i].type == 0:

                    if self.attaques[i].tempo_destruction == 0:

                        self.attaques[i].images["impacte"].position = \
                            (self.attaques[i].x_image+self.attaques[i].w_image//2-20,
                             self.attaques[i].y_image+self.attaques[i].h_image//2-20)

                    if self.attaques[i].tempo_destruction < 24:
                        self.attaques[i].tempo_destruction += 1
                        self.attaques[i].images["impacte"].position = \
                            (self.attaques[i].x_image+self.attaques[i].w_image//2-20,
                             self.attaques[i].y_image+self.attaques[i].h_image//2-20)
                        self.refresh_list.append([self.attaques[i].images["impacte"], 8])
                    else:
                        del self.attaques[i]
                        i -= 1

            i += 1

    # Méthode qui anime les sprite qui en ont besoin

    def animer_sprites(self, window, resolution):

        # Cette fonction se doit d'être très optimisée, afin de pouvoir gerer au mieux les animations nombreuses

        data = {"min-x": self.decalage[0]//64-1,
                "min-y": self.decalage[1]//64-1,
                "max-x": (self.decalage[0]+resolution["w"])//64+1,
                "max-y": (self.decalage[1]+resolution["h"])//64+1,
                "sprite-lave": sf.Sprite(TILESET_ANIME, (self.tempo//6*64, 0, 64, 64)),
                "sprite-brasier": sf.Sprite(TILESET_ANIME, (self.tempo//6*64, 64, 64, 64))}

        for x, y in self.blocs_importants["sprites_animes"]:
            if data["min-x"] <= x <= data["max-x"] and data["min-y"] <= y <= data["max-y"]:

                if self.blocs[x, y] == 8:
                    data["sprite-lave"].position = ((x*64)-self.decalage[0], (y*64)-self.decalage[1])
                    window.draw(data["sprite-lave"])

                elif self.blocs[x, y] == 12:
                    data["sprite-brasier"].position = ((x*64)-self.decalage[0], (y*64)-self.decalage[1])
                    window.draw(data["sprite-brasier"])

    # Méthode qui verifier si tout les brasiers sont allumés

    def brasiers_allumes(self):

        for bloc in self.blocs_importants["brasiers"]:
            if self.blocs[bloc] != 12:
                return False
        return True

    # Méthode qui ouvre la porte si tout les brasiers sont allumes, et qui sinon, la ferme

    def gerer_portes(self):

        display_list = list()

        if self.brasiers_allumes():
            for bloc in self.blocs_importants["portes"]:
                if self.blocs[bloc] == 9:
                    self.blocs[bloc] = 2
                    sprite = sf.Sprite(TILESET, (128, 0, 64, 64))
                    sprite.position = ((bloc[0]*64) % TEXTURE_MAX, (bloc[1]*64) % TEXTURE_MAX)
                    self.fond[(bloc[1]*64)//TEXTURE_MAX][(bloc[0]*64)//TEXTURE_MAX].draw(sprite)
                    display_list.append(((bloc[0]*64)//TEXTURE_MAX, (bloc[1]*64)//TEXTURE_MAX))

                if self.blocs[bloc] == 10:
                    self.blocs[bloc] = 3
                    sprite = sf.Sprite(TILESET, (192, 0, 64, 64))
                    sprite.position = ((bloc[0]*64) % TEXTURE_MAX, (bloc[1]*64) % TEXTURE_MAX)
                    self.fond[(bloc[1]*64)//TEXTURE_MAX][(bloc[0]*64)//TEXTURE_MAX].draw(sprite)
                    display_list.append(((bloc[0]*64)//TEXTURE_MAX, (bloc[1]*64)//TEXTURE_MAX))

        displayed = list()
        for item in display_list:
            if item not in displayed:
                self.fond[item[1]][item[0]].display()
                displayed.append(item)

    # Méthode qui déplace les monstres

    def deplacer_monstres(self):

        for monstre in self.monstres:

            if monstre.actif:

                # Pour les monstres aux déplacements simples

                if monstre.type == 0:

                    # Obtenir le déplacement sur l'axe horizontal

                    monstre.deplacement["x"] = 0

                    if monstre.x_hitbox < self.joueur.x_hitbox:
                        if monstre.x_hitbox+monstre.vitesse < self.joueur.x_hitbox:
                            monstre.deplacement["x"] = monstre.vitesse
                        else:
                            monstre.deplacement["x"] = self.joueur.x_hitbox-monstre.x_hitbox

                    elif monstre.x_hitbox > self.joueur.x_hitbox:
                        if monstre.x_hitbox-monstre.vitesse > self.joueur.x_hitbox:
                            monstre.deplacement["x"] = -monstre.vitesse
                        else:
                            monstre.deplacement["x"] = self.joueur.x_hitbox-monstre.x_hitbox

                    else:
                        monstre.deplacement["x"] = 0

                    # Obtenir le déplacement sur l'axe vertical

                    if TRAVERSABLE[self.blocs[monstre.x_hitbox//64, (monstre.y_hitbox+monstre.h_hitbox+1)//64]] and \
                       TRAVERSABLE[self.blocs[(monstre.x_hitbox+monstre.w_hitbox)//64, (monstre.y_hitbox+monstre.h_hitbox+1)//64]]:
                        if monstre.deplacement["y"] < 60:
                            monstre.deplacement["y"] += 2
                    else:
                        monstre.deplacement["y"] = 0

                    # Déplacer le monstre

                    monstre.deplacer(self)

                    # Infliger des dégats si le joueur se trouve à proximité

                    if monstre.collision(self.joueur):
                        self.joueur.vie -= monstre.degats

                    # Afficher le monstre

                    if monstre.deplacement["x"] > 0:
                        direction = "droite"
                    else:
                        direction = "gauche"

                    if monstre.deplacement["x"] != 0 or monstre.deplacement["y"] != 0:
                        evenement = "course"
                    else:
                        evenement = "arret"

                    if "course" in evenement:
                        monstre.images[direction][evenement][self.tempo//6].position = (monstre.x_image, monstre.y_image)
                        self.refresh_list.append([monstre.images[direction][evenement][self.tempo//6], 6])
                    else:
                        monstre.images[direction][evenement].position = (monstre.x_image, monstre.y_image)
                        self.refresh_list.append([monstre.images[direction][evenement], 6])

    # Méthode qui s'occupe d'effacer les monstres morts

    def gerer_mort_monstres(self):

        i = 0
        while i < len(self.monstres):
            if self.monstres[i].mort:
                del self.monstres[i]
                i -= 1
            i += 1

    # Méthode qui active les monstres visibles a l'écran

    def activer_monstres(self, resolution):

        camera = {"max-x": self.decalage[0]+resolution["w"],
                  "max-y": self.decalage[1]+resolution["h"]}

        for monstre in self.monstres:
            if monstre.x_image+monstre.w_image > self.decalage[0] and monstre.x_image < camera["max-x"] and \
               monstre.y_image+monstre.h_image > self.decalage[1] and monstre.y_image < camera["max-y"]:
                monstre.actif = True
            else:
                monstre.actif = False

    # Méthode qui detecte s'il faut créer une fenêtre de tutoriel et la créé

    def detecter_fenetre(self):

        # Detecte si le joueur marche sur le bon bloc, et si oui, créé une fenêtre

        a_effacer = list()
        for bloc in self.blocs_importants["fenetres"]:
            if self.joueur.collision((bloc[0]*64, bloc[1]*64, 64, 64)):
                a_effacer.append(bloc[2])
                with open("levels/"+("tuto" if self.mode_tutoriel else "level")+str(self.level)+".txt", "r") as fichier:
                    self.fenetre = Fenetre(fichier.read().split("\n.")[bloc[2]])

        # Si une fenêtre a été créée, efface tout les blocs lui correspondant de la liste des fenêtres potentielles

        for n in a_effacer:
            i = 0
            while i < len(self.blocs_importants["fenetres"]):
                if self.blocs_importants["fenetres"][i][2] == n:
                    del self.blocs_importants["fenetres"][i]
                    i -= 1
                i += 1

    # Méthode qui affiche la fenetre et gère le bouton pour la quitter

    def afficher_fenetre(self, window, resolution):

        if self.fenetre is not None:

            # Affiche la fenêtre

            self.fenetre.x = (resolution["w"]-self.fenetre.w)//2
            self.fenetre.y = 10

            sprite = sf.Sprite(self.fenetre.image)
            sprite.position = (self.fenetre.x, self.fenetre.y)
            sprite.color = sf.Color(255, 255, 255, 200)
            window.draw(sprite)

            # Vérifie si le joueur clique sur la croix pour fermer la fenêtre

            position_souris = sf.Mouse.get_position(window)

            if self.fenetre.x+self.fenetre.w > position_souris.x > self.fenetre.x+self.fenetre.w-12 and \
               self.fenetre.y < position_souris.y < self.fenetre.y+12 and \
               sf.Mouse.is_button_pressed(sf.Mouse.LEFT):
                self.fenetre = None

    # Méthode qui créer notamment les fleches des pieges

    def creer_attaques_pieges(self, resolution):

        for x, y in self.blocs_importants["pieges"]:
            if self.decalage[0]-64 < x*64 < self.decalage[0]+resolution["w"] and \
               self.decalage[1]-64 < y*64 < self.decalage[1]+resolution["h"]:

                # LANCES-FLECHES

                if 14 <= self.blocs[x, y] <= 17 and self.tempo_lent % 2 == 0 and self.tempo == 23:

                    attaque = Attaque(1)

                    # Calculer les coordonnees et obtenir les images de l'attaque, puis ajouter l'attaque a la liste

                    attaque.images = {"projectile": sf.Sprite(ATTAQUES, (40, 0, 10, 40))}
                    attaque.images["projectile"].origin = (5, 20)

                    if self.blocs[x, y] == 14:
                        attaque.x_hitbox = attaque.x_image = x*64+27
                        attaque.y_hitbox = attaque.y_image = y*64-40
                        attaque.w_image = attaque.w_hitbox = 10
                        attaque.h_image = attaque.h_hitbox = 40
                        attaque.deplacement["y"] = -25

                    elif self.blocs[x, y] == 15:
                        attaque.x_hitbox = attaque.x_image = x*64+27
                        attaque.y_hitbox = attaque.y_image = y*64+64
                        attaque.w_image = attaque.w_hitbox = 10
                        attaque.h_image = attaque.h_hitbox = 40
                        attaque.images["projectile"].rotation = 180
                        attaque.deplacement["y"] = 25

                    elif self.blocs[x, y] == 16:
                        attaque.x_hitbox = attaque.x_image = x*64+64
                        attaque.y_hitbox = attaque.y_image = y*64+27
                        attaque.w_image = attaque.w_hitbox = 40
                        attaque.h_image = attaque.h_hitbox = 10
                        attaque.images["projectile"].rotation = 90
                        attaque.deplacement["x"] = 25

                    elif self.blocs[x, y] == 17:
                        attaque.x_hitbox = attaque.x_image = x*64-40
                        attaque.y_hitbox = attaque.y_image = y*64+27
                        attaque.w_image = attaque.w_hitbox = 40
                        attaque.h_image = attaque.h_hitbox = 10
                        attaque.images["projectile"].rotation = 270
                        attaque.deplacement["x"] = -25

                    self.attaques.append(attaque)

    # Affiche la durée prise pour faire le niveau et le top 3 des meilleurs temps

    def afficher_temps_niveau(self, window, temps_actuel, raccourcis, resolution, session):

        # Mettre à jour la liste des meilleurs temps pour ce niveau

        if self.level > len(session.temps):
            for i in range(self.level-len(session.temps)):
                session.temps.append([None, None, None])
        session.temps[self.level-1].append(self.temps_niveau)
        session.temps[self.level-1].sort(key=lambda x: x if x is not None else time())
        session.temps[self.level-1] = session.temps[self.level-1][:3]

        # Obtenir la liste des meilleurs temps pouré ce niveau

        meilleurs_temps = [str(score)[:5] for score in session.temps[self.level-1]]

        # Boucle du menu

        while True:

            # Créer la page menu du programme puis l'afficher

            page = Page([Menu(("Meilleurs temps:\n"+"\n".join(meilleurs_temps),), 0, 0,
                              resolution["w"] if resolution["w"] > 1024 else 1024,
                              resolution["h"]-100 if resolution["h"] > 576 else 476, "textes"),
                         Menu(("Quitter", "Continuer"), 0, resolution["h"]-100 if resolution["h"] > 576 else 476,
                              resolution["w"] if resolution["w"] > 1024 else 1024, 100, flags=("horizontal",))], FOND)
            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Quitter

                if sortie["choix"] == [1, 0]:
                    session.placer_etage(self)
                    return False

                # Bouton: Continuer

                if sortie["choix"] == [1, 1]:
                    return True


            elif sortie == 0:
                continue
            elif sortie == 1:
                session.placer_etage(self)
                save_and_quit(0, session)
            else:
                continue
