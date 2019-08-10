# -*- coding:utf-8 -*

from page import *


class Attaque(EntiteMobile):

    def __init__(self, type_attaque, w_hitbox=0, h_hitbox=0):

        super(Attaque, self).__init__(w_hitbox=w_hitbox, h_hitbox=h_hitbox)

        self.type = type_attaque
        self.images = {"projectile": sf.Texture.create(1, 1), "impacte": sf.Texture.create(1, 1)}

        self.detruit = False
        self.tempo_destruction = 0
