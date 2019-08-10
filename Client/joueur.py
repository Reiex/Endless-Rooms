# -*- coding:utf_8 -*

from monstres import *
from time import time

image_joueur = sf.Image.from_file("images/joueur.png")
image_joueur.create_mask_from_color(sf.Color(255, 255, 255))

JOUEUR = sf.Texture.from_image(image_joueur)


class Joueur(EntiteMobile):

    def __init__(self):

        super(Joueur, self).__init__(w_image=64, h_image=128, w_hitbox=36, h_hitbox=122)

        # Tout les sprites du joueur

        self.images = self.charger_sprites()

        # Caractéristiques du joueur

        self.vitesse = 10

        self._vie = 6
        self._vie_maximum = 6
        self._invincible = {"temps": 0, "bool": False}
        self.duree_invincibilite = 1

        self.derniere_attaque = sf.Clock()
        self._temps_entre_attaques = 0.6
        self.degats = 1

    # ------------------------------------------------------------------------------------------------------------------
    # METHODES NORMALES
    # ------------------------------------------------------------------------------------------------------------------

    # Methode qui sert à ne pas encombrer __init__ pour charger les differents sprites du joueur

    @staticmethod
    def charger_sprites():
        return {
            "droite": {
                "course": [
                    sf.Sprite(JOUEUR, (0, 0, 64, 128)),
                    sf.Sprite(JOUEUR, (64, 0, 64, 128)),
                    sf.Sprite(JOUEUR, (128, 0, 64, 128)),
                    sf.Sprite(JOUEUR, (192, 0, 64, 128))],
                "course-attaque": [
                    sf.Sprite(JOUEUR, (256, 0, 64, 128)),
                    sf.Sprite(JOUEUR, (320, 0, 64, 128)),
                    sf.Sprite(JOUEUR, (384, 0, 64, 128)),
                    sf.Sprite(JOUEUR, (448, 0, 64, 128))],
                "saut": sf.Sprite(JOUEUR, (512, 0, 64, 128)),
                "saut-attaque": sf.Sprite(JOUEUR, (576, 0, 64, 128)),
                "arret": sf.Sprite(JOUEUR, (640, 0, 64, 128)),
                "arret-attaque": sf.Sprite(JOUEUR, (704, 0, 64, 128))},
            "gauche": {
                "course": [
                    sf.Sprite(JOUEUR, (0, 128, 64, 128)),
                    sf.Sprite(JOUEUR, (64, 128, 64, 128)),
                    sf.Sprite(JOUEUR, (128, 128, 64, 128)),
                    sf.Sprite(JOUEUR, (192, 128, 64, 128))],
                "course-attaque": [
                    sf.Sprite(JOUEUR, (256, 128, 64, 128)),
                    sf.Sprite(JOUEUR, (320, 128, 64, 128)),
                    sf.Sprite(JOUEUR, (384, 128, 64, 128)),
                    sf.Sprite(JOUEUR, (448, 128, 64, 128))],
                "saut": sf.Sprite(JOUEUR, (512, 128, 64, 128)),
                "saut-attaque": sf.Sprite(JOUEUR, (576, 128, 64, 128)),
                "arret": sf.Sprite(JOUEUR, (640, 128, 64, 128)),
                "arret-attaque": sf.Sprite(JOUEUR, (704, 128, 64, 128))}}

    # ------------------------------------------------------------------------------------------------------------------
    # ENCAPSULATIONS
    # ------------------------------------------------------------------------------------------------------------------

    # Encapsulation de self._vie en self.vie

    @property
    def vie(self):
        return self._vie

    @vie.setter
    def vie(self, nouvelle_vie):

        if not self.invincible or nouvelle_vie > self._vie:
            if nouvelle_vie < self._vie:
                self.invincible = True
            if nouvelle_vie < 0:
                nouvelle_vie = 0
            if nouvelle_vie > self.vie_maximum:
                nouvelle_vie = self.vie_maximum
            self._vie = nouvelle_vie

    # Encapsulation de self._invincibilite en self.invincibilite

    @property
    def invincible(self):

        if self._invincible["temps"]+self.duree_invincibilite < time():
            self._invincible["bool"] = False

        return self._invincible["bool"]

    @invincible.setter
    def invincible(self, invincible):

        self._invincible = {"temps": time(), "bool": invincible}

    # Encapsulation de self._vie_maximum en self.vie_maximum

    vie_maximum = property(lambda self: self._vie_maximum)

    @vie_maximum.setter
    def vie_maximum(self, nouvelle_vie_maximum):

        self._vie += nouvelle_vie_maximum-self._vie_maximum
        self._vie_maximum = nouvelle_vie_maximum

    # Encapsulation de self._temps_entre_attaques en self.temps_entre_attaques

    temps_entre_attaques = property(lambda self: self._temps_entre_attaques)

    @temps_entre_attaques.setter
    def temps_entre_attaques(self, nouveau_temps):

        if nouveau_temps < 0.15:
            nouveau_temps = 0.15

        self._temps_entre_attaques = nouveau_temps
