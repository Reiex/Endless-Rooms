# -*- coding:utf-8 -*

from attaques import *

image_monstres = sf.Image.from_file("images/monstres.png")
image_monstres.create_mask_from_color(sf.Color(255, 255, 255))

MONSTRES = sf.Texture.from_image(image_monstres)

DATA_MONSTRES = [{"vie_maximum": 4, "degats": 1, "vitesse": 4, "taille-px": [64, 64], "y-ligne": 0}]


class Monstre(EntiteMobile):

    def __init__(self, type_monstre=0, x_image=0, y_image=0, w_image=0, h_image=0, x_hitbox=0, y_hitbox=0, w_hitbox=0, h_hitbox=0):

        super(Monstre, self).__init__(x_image, y_image, w_image, h_image, x_hitbox, y_hitbox, w_hitbox, h_hitbox)

        self.actif = False
        self.type = type_monstre

        self.images = self.charger_sprites()

        self._vie = DATA_MONSTRES[type_monstre]["vie_maximum"]
        self.vie_maximum = DATA_MONSTRES[type_monstre]["vie_maximum"]
        self.mort = False
        self.degats = DATA_MONSTRES[type_monstre]["degats"]
        self.vitesse = DATA_MONSTRES[type_monstre]["vitesse"]

    # Methode pour charger les differents sprites en fonction du type de monstre

    def charger_sprites(self):

        y = DATA_MONSTRES[self.type]["y-ligne"]
        taille = DATA_MONSTRES[self.type]["taille-px"]

        return {
            "droite": {
                "course": [
                    sf.Sprite(MONSTRES, (0, y, taille[0], taille[1])),
                    sf.Sprite(MONSTRES, (taille[0], y, taille[0], taille[1])),
                    sf.Sprite(MONSTRES, (2*taille[0], y, taille[0], taille[1])),
                    sf.Sprite(MONSTRES, (3*taille[0], y, taille[0], taille[1]))],
                "arret": sf.Sprite(MONSTRES, (8*taille[0], y, taille[0], taille[1]))},
            "gauche": {
                "course": [
                    sf.Sprite(MONSTRES, (4*taille[0], y, taille[0], taille[1])),
                    sf.Sprite(MONSTRES, (5*taille[0], y, taille[0], taille[1])),
                    sf.Sprite(MONSTRES, (6*taille[0], y, taille[0], taille[1])),
                    sf.Sprite(MONSTRES, (7*taille[0], y, taille[0], taille[1]))],
                "arret": sf.Sprite(MONSTRES, (9*taille[0], y, taille[0], taille[1]))}}

    # ------------------------------------------------------------------------------------------------------------------
    # ENCAPSULATIONS
    # ------------------------------------------------------------------------------------------------------------------

    # Encapsulation de self._vie en self.vie

    vie = property(lambda self: self._vie)

    @vie.setter
    def vie(self, nouvelle_vie):

        if nouvelle_vie <= 0:
            self.mort = True
            self._vie = 0
        else:
            self._vie = nouvelle_vie
