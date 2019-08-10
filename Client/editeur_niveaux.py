# -*- coding:utf-8 -*

from demandes_serveur import *

interface_edit_image = sf.Image.from_file("images/interface_edit.png")
interface_edit_image.create_mask_from_color(sf.Color(255, 255, 255))

TILESET_EDIT = sf.Texture.from_file("images/tileset.png")
INTERFACE_EDIT = sf.Texture.from_image(interface_edit_image)


class EtageEdit:

    def __init__(self):

        self.fond = list()
        self.nom = str()

        self.taille = [0, 0]
        self.blocs = np.array([], np.uint16)
        self.decalage = [0, 0]

        self.joueur = {"x": int(), "y": int()}
        self.monstres = list()

        self.pseudo = str()
        self.password = str()

    # ------------------------------------------------------------------------------------------------------------------
    # MENU PRINCIPAL
    # ------------------------------------------------------------------------------------------------------------------

    # Methode principale lancée dès qu'on clique sur "Editeur de niveaux"

    def main(self, window, temps_actuel, raccourcis, resolution):

        # BOUCLE DU MENU

        continuer_menu = True

        while continuer_menu:

            # Initialiser la position du joueur à (None, None) afin de ne pas risquer un bug

            self.joueur["x"], self.joueur["y"] = None, None

            # Création du menu et affichage

            page = Page([Menu(("Nouveau niveau", "Modifier un niveau", "Gérer ses niveaux en ligne", "Retour"), 0, 0,
                              resolution["w"] if resolution["w"] >= 1024 else 1024,
                              resolution["h"] if resolution["h"] >= 576 else 576, "normal")])

            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Nouveau niveau

                if sortie["choix"] == [0, 0]:
                    if self.initialiser(window, temps_actuel, raccourcis, resolution) is not None:
                        self.editer(window, temps_actuel, raccourcis, resolution)

                # Bouton: Charger un niveau

                elif sortie["choix"] == [0, 1]:
                    if self.choisir_niveau(window, temps_actuel, raccourcis, resolution):
                        self.editer(window, temps_actuel, raccourcis, resolution)

                # Bouton: Gérer les niveaux en ligne

                elif sortie["choix"] == [0, 2]:
                    if self.connecter(window, temps_actuel, raccourcis, resolution):
                        self.choix_operation(window, temps_actuel, raccourcis, resolution)

                # Bouton: Retour

                elif sortie["choix"] == [0, 3]:
                    continuer_menu = False

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                continuer_menu = False

    # Recupere l'un des niveaux edités pour continuer a l'editer

    def choisir_niveau(self, window, temps_actuel, raccourcis, resolution):

        continuer_choix = True

        liste_etages = obtenir_liste_noms_etages()

        while continuer_choix:

            # Création du menu et affichage

            page = Page([Menu(liste_etages, 50, 50, resolution["w"]-100 if resolution["w"] >= 1024 else 924,
                              resolution["h"]-200 if resolution["h"] >= 576 else 376,
                              flags=("selection", "vertical", "defilant")),
                         Menu(("Retour", "Effacer", "Valider"), 0,
                              resolution["h"]-100 if resolution["h"] >= 576 else 476,
                              resolution["w"] if resolution["w"] >= 1024 else 1024, 100,
                              flags=("horizontal",))], FOND)

            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Retour

                if sortie["choix"] == [1, 0]:
                    continuer_choix = False

                # Bouton: Effacer

                if sortie["choix"] == [1, 1] and sortie["selection"][0] is not None:
                    remove("edit/"+liste_etages[sortie["selection"][0]]+".png")

                    liste_etages = obtenir_liste_noms_etages()

                # Bouton: Valider

                if sortie["choix"] == [1, 2] and sortie["selection"][0] is not None:
                    self.nom = liste_etages[sortie["selection"][0]]
                    self.charger_niveau(window, resolution)
                    return True

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                continuer_choix = False

        return False

    # ------------------------------------------------------------------------------------------------------------------
    # CREATION DU NIVEAU
    # ------------------------------------------------------------------------------------------------------------------

    # Demande la taille du niveau à l'utilisateur et modifie self en conséquences

    def initialiser(self, window, temps_actuel, raccourcis, resolution):

        continuer_menu = True

        while continuer_menu:

            # Création du menu et affichage

            page = Page([Menu((("Largeur ?(entre 30 et 300):", "_", 3), ("Hauteur ?(entre 30 et 300):", "_", 3)), 0, 0,
                              resolution["w"] if resolution["w"] >= 1024 else 1024,
                              resolution["h"]-100 if resolution["h"] >= 576 else 476, "saisies"),
                         Menu(("Retour", "Valider"), 0, resolution["h"]-100 if resolution["h"] >= 576 else 476,
                              resolution["w"] if resolution["w"] >= 1024 else 1024, 100, "normal", ("horizontal",))])

            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Retour

                if sortie["choix"] == [1, 0]:
                    return None

                # Bouton: Valider

                if sortie["choix"] == [1, 1]:

                    # Vérifier la sortie et l'appliquer à self.taille (+2 pour inclure les bords non modifiables)

                    try:
                        self.taille = [int(sortie["valeur"][0][0]), int(sortie["valeur"][0][1])]
                        assert 30 <= self.taille[0] <= 300 >= self.taille[1] >= 30
                        self.taille[0] += 2
                        self.taille[1] += 2
                    except (IndexError, ValueError, AssertionError):
                        continue

                    # Création du tableau du niveau de façon à avoir des bords pour la map et chargement des fonds

                    self.blocs.resize(self.taille)
                    for y in range(self.taille[1]):
                        for x in range(self.taille[0]):
                            if y == 0 or y == self.taille[1]-1 or x == 0 or x == self.taille[0]-1:
                                self.blocs[x, y] = 1
                            else:
                                self.blocs[x, y] = 0

                    self.charger_fonds(window=window, resolution=resolution)
                    self.nom = str()

                    return not None

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                return None

    # Methode qui charge un niveau a partir d'une image enregistrée dans /edit pour ensuite l'editer

    def charger_niveau(self, window, resolution):

        # Obtenir les informations de base

        image = sf.Image.from_file("edit/"+self.nom+".png")
        self.taille = [image.width, image.height]
        self.blocs = np.array([], np.uint16)
        self.blocs.resize(self.taille)
        self.monstres = list()

        # Obtenir le type de chaque bloc

        for x in range(self.taille[0]):
            for y in range(self.taille[1]):

                chaine = "{r},{g},{b}".format(r=image[x, y].r, g=image[x, y].g, b=image[x, y].b)
                if chaine in BLOCS_COULEUR.keys():
                    self.blocs[x, y] = BLOCS_COULEUR[chaine]

                    if image[x, y] == sf.Color(50, 50, 50):
                        self.joueur = {"x": x, "y": y}

                elif image[x, y].g == image[x, y].r == 255 and image[x, y].b != 255:
                    self.blocs[x, y] = 0
                    self.monstres.append({"x": x, "y": y, "type": image[x, y].b})

        # Dessiner les fonds

        self.charger_fonds(window=window, resolution=resolution)

    # Appelée dans self.initialiser, cette méthode permet de créer les chunks

    @ecran_de_chargement("Chargement")
    def charger_fonds(self, **kwargs):

        self.fond = list()

        for y in range((self.taille[1]*64)//TEXTURE_MAX+1):
            self.fond.append(list())
            for x in range((self.taille[0]*64)//TEXTURE_MAX+1):
                self.fond[y].append(sf.RenderTexture(TEXTURE_MAX, TEXTURE_MAX))

        for y in range(self.taille[1]):
            for x in range(self.taille[0]):
                sprite = sf.Sprite(TILESET_EDIT, ((self.blocs[x, y] % 10)*64, (self.blocs[x, y]//10)*64, 64, 64))
                sprite.position = ((x*64) % TEXTURE_MAX, (y*64) % TEXTURE_MAX)
                self.parametrer_shader_ombre(x, y)
                self.fond[(y*64)//TEXTURE_MAX][(x*64)//TEXTURE_MAX].draw(sprite, sf.RenderStates(shader=SHADER_OMBRE))

        for item in self.fond:
            for chunk in item:
                chunk.display()

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

    # Créer une image du niveau créé et l'enregistre, demande un nom si le niveau n'en a pas

    def sauvegarder(self, window, temps_actuel, raccourcis, resolution):

        if self.nom == str():

            demander_nom = True
            nom_deja_pris = False

            while demander_nom:

                # Creer la page du menu de création de session puis l'afficher

                if not nom_deja_pris:

                    page = Page([Menu(("Nom du niveau:", "_", 10), 0, 0,
                                      resolution["w"] if resolution["w"] >= 1024 else 1024,
                                      resolution["h"]-100 if resolution["h"] >= 576 else 476, "input"),
                                 Menu(("Valider",), 0,
                                      resolution["h"]-100 if resolution["h"] >= 576 else 476,
                                      resolution["w"] if resolution["w"] >= 1024 else 1024, 100, flags=("horizontal",))], FOND)

                else:

                    page = Page([Menu(("Le nom que vous avez saisi\nest déjà utilisé.",), 0, 0,
                                      resolution["w"] if resolution["w"] >= 1024 else 1024, 150, "textes"),
                                 Menu(("Nom du niveau:", "_", 10), 0, 150,
                                      resolution["w"] if resolution["w"] >= 1024 else 1024,
                                      resolution["h"]-250 if resolution["h"] >= 576 else 326, "input"),
                                 Menu(("Valider",), 0,
                                      resolution["h"]-100 if resolution["h"] >= 576 else 476,
                                      resolution["w"] if resolution["w"] >= 1024 else 1024, 100, flags=("horizontal",))], FOND)

                sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

                # Traiter la sortie

                if isinstance(sortie, dict):

                    # Bouton: Valider

                    num = 1 if nom_deja_pris else 0

                    if sortie["choix"] == [1+num, 0]:
                        if sortie["valeur"][num] != str() and sortie["valeur"][num] not in obtenir_liste_noms_etages():
                            self.nom = sortie["valeur"][num]
                            demander_nom = False
                        elif sortie["valeur"][num] in obtenir_liste_noms_etages():
                            nom_deja_pris = True

                elif sortie == 0:
                    continue
                elif sortie == 1:
                    continue
                else:
                    continue

        bloc_couleur = {bloc: couleur for couleur, bloc in BLOCS_COULEUR.items()}

        image = sf.Image.create(self.taille[0], self.taille[1])
        for y in range(self.taille[1]):
            for x in range(self.taille[0]):
                couleur = bloc_couleur[self.blocs[x, y]].split(",")
                image[x, y] = sf.Color(int(couleur[0]), int(couleur[1]), int(couleur[2]))

        for monstre in self.monstres:
            image[monstre["x"], monstre["y"]] = sf.Color(255, 255, monstre["type"])

        if self.joueur["x"]is not None and self.joueur["y"] is not None:
            image[self.joueur["x"], self.joueur["y"]] = sf.Color(50, 50, 50)

        image.to_file("edit/"+self.nom+".png")

    # Demande a l'utilisateur s'il veut sauvegarder via un menu, retourne True s'il a cliqué sur oui, sinon False

    def demander_sauvegarder(self, window, temps_actuel, raccourcis, resolution):

        continuer_demande = True

        while continuer_demande:

            # Créer la page menu du programme puis l'afficher

            page = Page([Menu(("Sauvegarder ?",), 0, 0, resolution["w"] if resolution["w"] >= 1024 else 1024,
                              resolution["h"]-100 if resolution["h"] >= 576 else 476, "textes"),
                         Menu(("Non", "Oui"), 0, resolution["h"]-100 if resolution["h"] >= 576 else 476,
                              resolution["w"] if resolution["w"] >= 1024 else 1024,
                              100, flags=("horizontal",))], FOND)

            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Non

                if sortie["choix"] == [1, 0]:
                    return False

                # Bouton: Oui

                if sortie["choix"] == [1, 1]:
                    possible_sauvegarder = True if self.joueur != {"x": None, "y": None} else False

                    while not possible_sauvegarder:

                        # Créer la page menu du programme puis l'afficher

                        page = Page([Menu(("Impossible de sauvegarder.\nAucun spawn n'a été trouvé",),
                                          0, 0, resolution["w"] if resolution["w"] >= 1024 else 1024,
                                          resolution["h"]-100 if resolution["h"] >= 576 else 476, "textes"),
                                     Menu(("Retour",), 0, resolution["h"]-100 if resolution["h"] >= 576 else 476,
                                          resolution["w"] if resolution["w"] >= 1024 else 1024,
                                          100, flags=("horizontal",))], FOND)

                        sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

                        # Traiter la sortie

                        if isinstance(sortie, dict):

                            # Bouton: Retour

                            if sortie["choix"] == [1, 0]:
                                return None

                        elif sortie == 0:
                            continue
                        elif sortie == 1:
                            exit(0)
                        else:
                            continue

                    return True

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                continue

    # ------------------------------------------------------------------------------------------------------------------
    # EDITION DU NIVEAU
    # ------------------------------------------------------------------------------------------------------------------

    # Boucle principale: Edition d'un niveau

    def editer(self, window, temps_actuel, raccourcis, resolution):

        continuer_edition = True
        deplacement_cadre = {"x-mouse-start": 0, "y-mouse-start": 0,
                             "x-cadre-start": 0, "y-cadre-start": 0, "actif": False}
        position_souris = [0, 0]
        data_interface = {"barre-active": 0, "bloc-actif": None,
                          "bouton-action": [["barre0", "barre1", "barre2", "barre3", "spawn"],
                                            [0, 1, 13, 18],
                                            [4, 5, 6, 7, 8, 14, 15, 16, 17],
                                            ["porte2", "porte9", 11, 12],
                                            ["monstre0"]]}
        data_interface["barres"] = self.creer_images_barres(data_interface)

        while continuer_edition:

            # Rafraichir l'image

            window.display()
            gerer_fps(temps_actuel)

            # Gestion des évenements

            for event in window.events:

                if isinstance(event, sf.ResizeEvent):
                    resolution["w"], resolution["h"] = event.size.x, event.size.y
                    window.view.reset((0, 0, resolution["w"], resolution["h"]))

                if isinstance(event, sf.MouseButtonEvent):
                    if event.button == sf.Mouse.RIGHT and event.pressed:
                        deplacement_cadre = {"x-mouse-start": event.position.x, "y-mouse-start": event.position.y,
                                             "x-cadre-start": self.decalage[0], "y-cadre-start": self.decalage[1],
                                             "actif": True}
                    if event.button == sf.Mouse.RIGHT and event.released:
                        deplacement_cadre["actif"] = False

                    if event.button == sf.Mouse.LEFT and event.released:
                        if not self.gerer_boutons(event, data_interface):
                            self.placer_blocs(data_interface["bloc-actif"], position_souris)

                if isinstance(event, sf.MouseMoveEvent):
                    position_souris = [event.position.x, event.position.y]
                    if deplacement_cadre["actif"]:
                        self.decalage = [deplacement_cadre["x-cadre-start"] +
                                         (deplacement_cadre["x-mouse-start"]-event.position.x),
                                         deplacement_cadre["y-cadre-start"] +
                                         (deplacement_cadre["y-mouse-start"]-event.position.y)]

                if isinstance(event, sf.CloseEvent):
                    reponse = self.demander_sauvegarder(window, temps_actuel, raccourcis, resolution)
                    if reponse is not None and reponse:
                        self.sauvegarder(window, temps_actuel, raccourcis, resolution)
                    if reponse is not None:
                        exit(0)

                # MENU DE L'EDITION

                if isinstance(event, sf.KeyEvent):
                    if event.code == raccourcis["menu"][0] and event.released:

                        # Prendre une capture d'ecran comme fond de la page

                        window.display()
                        fond_page = window.capture()
                        menu = True
                        fond_menu = sf.Sprite(sf.Texture.from_image(INTERFACE_IMAGE), (0, 108, 1024, 576))

                        # Boucle du menu

                        while menu:

                            # Creer la page du menu du jeu puis l'afficher

                            page = Page([Menu(("Continuer", "Recommencer le niveau", "Sauvegarder", "Quitter"),
                                              (resolution["w"]-1024)//2, (resolution["h"]-576)//2,
                                              1024, 576, fond=fond_menu)], fond_page)
                            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

                            # Traiter la sortie

                            if isinstance(sortie, dict):

                                # Bouton: Continuer

                                if sortie["choix"] == [0, 0]:
                                    menu = False

                                # Bouton: Recommencer le niveau

                                if sortie["choix"] == [0, 1]:
                                    self.nom = str()
                                    self.blocs = np.array([], np.uint16)
                                    self.blocs.resize(self.taille)
                                    for y in range(self.taille[1]):
                                        for x in range(self.taille[0]):
                                            if y == 0 or y == self.taille[1]-1 or x == 0 or x == self.taille[0]-1:
                                                self.blocs[x, y] = 1
                                    self.joueur = {"x": None, "y": None}
                                    self.monstres = list()
                                    self.charger_fonds()
                                    menu = False

                                # Bouton: Sauvegarder

                                if sortie["choix"] == [0, 2]:
                                    self.sauvegarder(window, temps_actuel, raccourcis, resolution)

                                # Bouton: Quitter

                                if sortie["choix"] == [0, 3]:
                                    reponse = self.demander_sauvegarder(window, temps_actuel, raccourcis, resolution)
                                    if reponse is not None and reponse:
                                        self.sauvegarder(window, temps_actuel, raccourcis, resolution)
                                    if reponse is not None:
                                        continuer_edition = False
                                        menu = False

                            elif sortie == 0:
                                continue
                            elif sortie == 1:
                                reponse = self.demander_sauvegarder(window, temps_actuel, raccourcis, resolution)
                                if reponse is not None and reponse:
                                    self.sauvegarder(window, temps_actuel, raccourcis, resolution)
                                if reponse is not None:
                                    exit(0)
                            else:
                                menu = False

            # Gestion de l'edition (toutes les fonctions nécessaires)

            self.corriger_position_cadre(resolution)
            self.afficher_fond(window, resolution)
            self.afficher_bloc_selectionne(window, data_interface["bloc-actif"], position_souris)
            self.afficher_interface(window, position_souris, data_interface)

    # Modifie la position du cadre pour qu'il soit dans la map

    def corriger_position_cadre(self, resolution):

        if self.decalage[0]+resolution["w"] > self.taille[0]*64+100:
            self.decalage[0] = self.taille[0]*64-resolution["w"]+100
        elif self.decalage[0] < -100:
            self.decalage[0] = -100

        if self.decalage[1]+resolution["h"] > self.taille[1]*64+100:
            self.decalage[1] = self.taille[1]*64-resolution["h"]+100
        elif self.decalage[1] < -100:
            self.decalage[1] = -100

    # Affiche le fond sur la fenêtre

    def afficher_fond(self, window, resolution):

        # Netoyer l'ecran

        window.clear(VALEUR_NOIR)

        # Dessiner le fond

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

        # Dessiner le joueur s'il est dans la fenêtre

        if self.joueur["x"] is not None and self.joueur["y"] is not None:
            if self.decalage[0]-64 < self.joueur["x"]*64 < self.decalage[0]+resolution["w"] and \
               self.decalage[1]-64 < self.joueur["y"]*64 < self.decalage[1]+resolution["h"]:
                sprite = sf.Sprite(JOUEUR, (640, 0, 64, 128))
                sprite.position = (self.joueur["x"]*64-self.decalage[0], self.joueur["y"]*64-self.decalage[1])
                window.draw(sprite)

        # Dessiner les monstres qui sont dans la fenêtre

        for monstre in self.monstres:
            taille = DATA_MONSTRES[monstre["type"]]["taille-px"]
            if self.decalage[0]-taille[0] < monstre["x"]*64 < self.decalage[0]+resolution["w"] and \
               self.decalage[1]-taille[1] < monstre["y"]*64 < self.decalage[1]+resolution["h"]:
                sprite = sf.Sprite(MONSTRES, (0, DATA_MONSTRES[monstre["type"]]["y-ligne"], taille[0], taille[1]))
                sprite.position = (monstre["x"]*64-self.decalage[0], monstre["y"]*64-self.decalage[1])
                window.draw(sprite)

    # Retourne les barres de l'interface sous forme d'une liste de sf.RenderTexture

    @staticmethod
    def creer_images_barres(data_interface):

        # Créer un rectangle qu'il suffira de redimensionner et qui sert de fond a la barre

        fond_barre = sf.RectangleShape()
        fond_barre.outline_color = sf.Color(0, 0, 0)
        fond_barre.outline_thickness = 2
        fond_barre.fill_color = sf.Color(200, 200, 200)
        fond_barre.position = (2, 2)

        # Créer un carré qui sert de fond de bouton

        carre = sf.RectangleShape()
        carre.size = (68, 68)
        carre.outline_color = sf.Color(0, 0, 0)
        carre.outline_thickness = 2

        # Pour chaque barre, coller le fond puis coller les fonds de boutons puis les images des boutons

        liste_barres = list()

        for i, barre in enumerate(data_interface["bouton-action"]):
            liste_barres.append(sf.RenderTexture(76*len(barre)+4, 80))
            fond_barre.size = (76*len(barre), 76)
            liste_barres[i].draw(fond_barre)
            for j, bouton in enumerate(barre):
                carre.position = (6+76*j, 6)
                liste_barres[i].draw(carre)
                sprite = sf.Sprite(INTERFACE_EDIT, (j*64, i*64, 64, 64))
                sprite.position = (8+76*j, 8)
                liste_barres[i].draw(sprite)
            liste_barres[i].display()

        return liste_barres

    # Afficher les barres de choix des blocs

    @staticmethod
    def afficher_interface(window, position_souris, data_interface):

        # Créer un carré de fond bleu qui servira de fond au possible bouton selectionné

        carre = sf.RectangleShape()
        carre.size = (68, 68)
        carre.outline_color = sf.Color(0, 0, 0)
        carre.outline_thickness = 2
        carre.fill_color = sf.Color(150, 200, 255)

        # Dessiner la barre principale

        window.draw(sf.Sprite(data_interface["barres"][0].texture))

        # Redessiner le bouton selectionné avec le fond bleu si ce bouton se trouve sur la barre principale

        for i, bouton in enumerate(data_interface["bouton-action"][0]):
            if 6+76*i < position_souris[0] < 74+76*i and 6 < position_souris[1] < 74:
                carre.position = (6+76*i, 6)
                window.draw(carre)
                sprite = sf.Sprite(INTERFACE_EDIT, (i*64, 0, 64, 64))
                sprite.position = (8+76*i, 8)
                window.draw(sprite)

        # Dessiner la barre secondaire

        if data_interface["barre-active"] != 0:
            sprite = sf.Sprite(data_interface["barres"][data_interface["barre-active"]].texture)
            sprite.position = (0, 82)
            window.draw(sprite)

            # Redessiner le bouton selectionné avec le fond bleu si ce bouton se trouve sur la barre secondaire

            for i, bouton in enumerate(data_interface["bouton-action"][data_interface["barre-active"]]):
                if 6+76*i < position_souris[0] < 74+76*i and 88 < position_souris[1] < 156:
                    carre.position = (6+76*i, 88)
                    window.draw(carre)
                    sprite = sf.Sprite(INTERFACE_EDIT, (i*64, data_interface["barre-active"]*64, 64, 64))
                    sprite.position = (8+76*i, 90)
                    window.draw(sprite)

    # Gerer les cliques sur la barre de menu

    @staticmethod
    def gerer_boutons(event, data_interface):

        # Repérer s'il y a un bouton de la barre brincipale cliqué

        for i, bouton in enumerate(data_interface["bouton-action"][0]):
            if 6+76*i < event.position.x < 74+76*i and 6 < event.position.y < 74:

                if "barre" in bouton:  # Si le bouton mène a une autre barre
                    if data_interface["barre-active"] != int(bouton.replace("barre", ""))+1:
                        data_interface["barre-active"] = int(bouton.replace("barre", ""))+1
                    else:
                        data_interface["barre-active"] = 0

                else:  # Si le bouton sert directement a placer un objet
                    data_interface["bloc-actif"] = bouton

                return True

        # Repérer s'il y a une barre secondaire active, et si oui, si un de ses boutons est cliqué

        if data_interface["barre-active"] != 0:
            for i, bouton in enumerate(data_interface["bouton-action"][data_interface["barre-active"]]):
                if 6+76*i < event.position.x < 74+76*i and 88 < event.position.y < 156:
                    data_interface["bloc-actif"] = bouton
                    return True

        return False

    # Afficher sur le fond le bloc en transparence

    def afficher_bloc_selectionne(self, window, objet, position_souris):

        # Créer une variable sprite pour calmer mon IDE enragé et calculer la position du bloc pointé

        sprites = list()
        position = ((self.decalage[0]+position_souris[0])//64, (self.decalage[1]+position_souris[1])//64)

        # Si c'est un bloc spécial

        if isinstance(objet, str):

            if objet == "spawn":  # Spawn
                sprites = [sf.Sprite(JOUEUR, (640, 0, 64, 64)),
                           sf.Sprite(JOUEUR, (640, 64, 64, 64))]
                sprites[0].position = (position[0]*64-self.decalage[0], position[1]*64-self.decalage[1])
                sprites[1].position = (position[0]*64-self.decalage[0], position[1]*64-self.decalage[1]+64)

            elif "porte" in objet:  # Portes
                base = int(objet.replace("porte", ""))
                sprites = [sf.Sprite(TILESET_EDIT, ((base % 10)*64, (base//10)*64, 64, 64)),
                           sf.Sprite(TILESET_EDIT, (((base+1) % 10)*64, ((base+1)//10)*64, 64, 64))]
                sprites[0].position = (position[0]*64-self.decalage[0], position[1]*64-self.decalage[1]+64)
                sprites[1].position = (position[0]*64-self.decalage[0], position[1]*64-self.decalage[1])

            elif "monstre" in objet:  # Monstres
                type_monstre = int(objet.replace("monstre", ""))
                y_cadre = DATA_MONSTRES[type_monstre]["y-ligne"]
                taille = DATA_MONSTRES[type_monstre]["taille-px"]
                sprites = list()
                for y in range(taille[1]//64):
                    for x in range(taille[0]//64):
                        sprites.append(sf.Sprite(MONSTRES, (x*64, y_cadre+y*64, 64, 64)))
                        sprites[y*taille[1]//64+x].position = (position[0]*64-self.decalage[0]+x*64,
                                                               position[1]*64-self.decalage[1]+y*64)

        # Si c'est un bloc normal

        elif isinstance(objet, int):
            sprites = [sf.Sprite(TILESET_EDIT, ((objet % 10)*64, (objet//10)*64, 64, 64))]
            sprites[0].position = (position[0]*64-self.decalage[0], position[1]*64-self.decalage[1])

        # Dessiner le(s) sprite(s)

        if objet is not None:
            for sprite in sprites:
                if 0 < (sprite.position.x+self.decalage[0])//64 < self.taille[0]-1 and \
                   0 < (sprite.position.y+self.decalage[1])//64 < self.taille[1]-1:
                    sprite.color = sf.Color(255, 255, 255, 125)
                    window.draw(sprite)

    # Activé lors d'un clic et change le fond et le tableau de blocs pour placer les blocs

    def placer_blocs(self, objet, position_souris):

        # Créer une variable blocs pour calmer mon IDE enragé et calculer la position du bloc pointé

        blocs = list()
        liste_displays = list()
        position = ((self.decalage[0]+position_souris[0])//64, (self.decalage[1]+position_souris[1])//64)

        # CREER LES SPRITES À AFFICHER

        if isinstance(objet, str):

            # Spawn

            if objet == "spawn":
                if 0 < position[0] < self.taille[0]-1 and 0 < position[1] < self.taille[1]-2:
                    self.joueur = {"x": position[0], "y": position[1]}
                    blocs = [{"id-bloc": None, "position": position},
                             {"id-bloc": None, "position": (position[0], position[1]+1)}]

            # Portes

            elif "porte" in objet:
                base = int(objet.replace("porte", ""))
                blocs = [{"id-bloc": base, "position": (position[0], position[1]+1)},
                         {"id-bloc": base+1, "position": position}]

            # Monstres

            elif "monstre" in objet:

                type_monstre = int(objet.replace("monstre", ""))
                taille = DATA_MONSTRES[type_monstre]["taille-px"]

                if 0 < position[0] and position[0]*64+taille[0] <= self.taille[0]*64-64 and \
                   0 < position[1] and position[1]*64+taille[1] <= self.taille[1]*64-64:

                    if not [True for monstre in self.monstres if (monstre["x"], monstre["y"]) == position]:
                        self.monstres.append({"x": position[0], "y": position[1], "type": type_monstre})

                        blocs = list()
                        for x in range(taille[0]//64):
                            for y in range(taille[1]//64):
                                blocs.append({"id-bloc": None, "position": (position[0]+x, position[1]+y)})
                                print("Prout")

        # Blocs normaux

        elif isinstance(objet, int):
            blocs = [{"id-bloc": objet, "position": position}]

        # AFFICHER LES SPRITES ET VERIFIER S'ILS NE REMPLACENT PAS D'AUTRES BLOCS

        for bloc in blocs:
            if 0 < bloc["position"][0] < self.taille[0]-1 and 0 < bloc["position"][1] < self.taille[1]-1:

                # Effacer la porte s'il y a collision du bloc placé avec une porte

                if self.blocs[bloc["position"]] in LISTE_PORTES[0]:  # S'il y a collision avec le bas de la porte
                    self.blocs[bloc["position"][0], bloc["position"][1]-1] = 0

                elif self.blocs[bloc["position"]] in LISTE_PORTES[1]:  # S'il y a collision avec le haut de la porte
                    self.blocs[bloc["position"][0], bloc["position"][1]+1] = 0

                if bloc["id-bloc"] is not None:

                    # Effacer le monstre s'il y a collision du bloc placé avec un monstre

                    del_list = list()
                    for i, monstre in enumerate(self.monstres):
                        if not (monstre["x"] > bloc["position"][0] or
                                bloc["position"][0] >= monstre["x"]+DATA_MONSTRES[monstre["type"]]["taille-px"][0]/64 or
                                monstre["y"] > bloc["position"][1] or
                                bloc["position"][1] >= monstre["y"]+DATA_MONSTRES[monstre["type"]]["taille-px"][1]/64):
                            del_list.append(i)
                    for i in del_list:
                        del self.monstres[i]

                    # Effacer le joueur s'il y a collision du bloc placé avec le joueur

                    if (self.joueur["x"], self.joueur["y"]) != (None, None):
                        if (self.joueur["x"], self.joueur["y"]) == bloc["position"] or \
                           (self.joueur["x"], self.joueur["y"]+1) == bloc["position"]:
                            self.joueur["x"], self.joueur["y"] = None, None

                    # Placer le bloc

                    self.blocs[bloc["position"]] = bloc["id-bloc"]

                else:

                    # Remplacer le bloc par du vide car c'est une entité mobile qui est placée

                    self.blocs[bloc["position"]] = 0

                # Afficher le sprite et les 8 autours de lui afin de mettre a jour les ombres

                for x in range(bloc["position"][0]-1, bloc["position"][0]+2):
                    for y in range(bloc["position"][1]-1, bloc["position"][1]+2):

                        sprite = sf.Sprite(TILESET_EDIT, ((self.blocs[x, y] % 10)*64, (self.blocs[x, y]//10)*64, 64, 64))
                        sprite.position = ((x*64) % TEXTURE_MAX, (y*64) % TEXTURE_MAX)
                        self.parametrer_shader_ombre(x, y)
                        self.fond[(y*64)//TEXTURE_MAX][(x*64)//TEXTURE_MAX].draw(sprite, sf.RenderStates(shader=SHADER_OMBRE))

                        if ((x*64)//TEXTURE_MAX, (y*64)//TEXTURE_MAX) not in liste_displays:
                            liste_displays.append(((x*64)//TEXTURE_MAX, (y*64)//TEXTURE_MAX))

        for texture in liste_displays:
            self.fond[texture[1]][texture[0]].display()

    # ------------------------------------------------------------------------------------------------------------------
    # GESTION DU NIVEAU EN LIGNE
    # ------------------------------------------------------------------------------------------------------------------

    # Inscrire / Identifier l'utilisateur

    def connecter(self, window, temps_actuel, raccourcis, resolution):

        message_erreur = "Le serveur est déconnecté.\nVeuillez réessayer plus tard."
        continuer_menu = True
        mode_inscription = False
        champs_de_saisies = (("Pseudo:", "_", 15), ("Mot de passe:", "_", 20))

        while continuer_menu:

            # Création du menu et affichage

            page = Page([Menu(("S'inscrire", "Se connecter"), 0, 0,
                              resolution["w"] if resolution["w"] >= 1024 else 1024, 80, "normal", ("horizontal",)),
                         Menu(champs_de_saisies, 0, 80, resolution["w"] if resolution["w"] >= 1024 else 1024,
                              resolution["h"]-160 if resolution["h"] >= 576 else 416, "saisies"),
                         Menu(("Retour", "Valider"), 0, resolution["h"]-80 if resolution["h"] >= 576 else 496,
                              resolution["w"] if resolution["w"] >= 1024 else 1024, 80, "normal", ("horizontal",))])

            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: S'inscrire

                if sortie["choix"] == [0, 0]:
                    mode_inscription = True
                    champs_de_saisies = (("Pseudo:", "_", 15), ("Mot de passe:", "_", 20),
                                         ("Confirmer mot de passe:", "_", 20))

                # Bouton: Se connecter

                if sortie["choix"] == [0, 1]:
                    mode_inscription = False
                    champs_de_saisies = (("Pseudo:", "_", 15), ("Mot de passe:", "_", 20))

                # Bouton: Retour

                if sortie["choix"] == [2, 0]:
                    return False

                # Bouton: Valider

                if sortie["choix"] == [2, 1]:
                    if mode_inscription:
                        if sortie["valeur"][1][1] == sortie["valeur"][1][2] != str() != sortie["valeur"][1][0]:
                            verification = inscription_bdd(sortie["valeur"][1][0], sortie["valeur"][1][1],
                                                           window=window, resolution=resolution)
                            if verification == "Error":
                                afficher_message(window, temps_actuel, raccourcis, resolution, message_erreur)
                                return False
                            elif verification:
                                self.pseudo = sortie["valeur"][1][0]
                                self.password = sortie["valeur"][1][1]
                                return True
                    else:
                        verification = verification_connexion_bdd(sortie["valeur"][1][0], sortie["valeur"][1][1],
                                                                  window=window, resolution=resolution)
                        if verification == "Error":
                            afficher_message(window, temps_actuel, raccourcis, resolution, message_erreur)
                            return False
                        elif verification:
                            self.pseudo = sortie["valeur"][1][0]
                            self.password = sortie["valeur"][1][1]
                            return True

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                return False

    # Faire choisir à l'utilisateur s'il veut ajouter un niveau en ligne ou en supprimer un

    def choix_operation(self, window, temps_actuel, raccourcis, resolution):

        continuer_menu = True

        while continuer_menu:

            # Création du menu et affichage

            page = Page([Menu(("Mettre un niveau en ligne", "Supprimer un niveau mis en ligne", "Retour"), 0, 0,
                              resolution["w"] if resolution["w"] >= 1024 else 1024,
                              resolution["h"] if resolution["h"] >= 576 else 576, "normal")])

            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Mettre un niveau en ligne

                if sortie["choix"] == [0, 0]:
                    nom_fichier = choisir_niveau(window, temps_actuel, raccourcis, resolution)
                    if nom_fichier is not None:
                        enregistrer_niveau_bdd(self.pseudo, self.password, nom_fichier+".png",
                                               window=window, resolution=resolution)

                # Bouton: Supprimer un niveau mis en ligne

                elif sortie["choix"] == [0, 1]:
                    self.choisir_niveau_supprimer(window, temps_actuel, raccourcis, resolution)

                # Bouton: Retour

                elif sortie["choix"] == [0, 2]:
                    continuer_menu = False

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                continuer_menu = False

    # Faire choisir à l'utilisateur le niveau qu'il veut supprimer parmis les niveaux qu'il a mis en ligne

    def choisir_niveau_supprimer(self, window, temps_actuel, raccourcis, resolution):

        continuer_choix = True

        while continuer_choix:

            # Obtenir la liste des niveaux de l'utilisateur mis en ligne

            liste_id_niveaux = list()
            liste_nom_niveaux = list()
            liste_niveaux = obtenir_liste_niveaux_bdd(window=window, resolution=resolution)
            for niveau in liste_niveaux:
                if niveau[1].split(" - ")[1] == self.pseudo:
                    liste_id_niveaux.append(niveau[0])
                    liste_nom_niveaux.append(niveau[1].split(" - ")[0])

            # Création du menu et affichage

            page = Page([Menu(liste_nom_niveaux, 50, 50, resolution["w"]-100 if resolution["w"] >= 1024 else 924,
                              resolution["h"]-200 if resolution["h"] >= 576 else 376,
                              flags=("selection", "vertical", "defilant")),
                         Menu(("Retour", "Valider"), 0,
                              resolution["h"]-100 if resolution["h"] >= 576 else 476,
                              resolution["w"] if resolution["w"] >= 1024 else 1024, 100,
                              flags=("horizontal",))], FOND)

            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Retour

                if sortie["choix"] == [1, 0]:
                    continuer_choix = False

                # Bouton: Valider

                if sortie["choix"] == [1, 1] and sortie["selection"][0] is not None:
                    id_niveau = liste_id_niveaux[sortie["selection"][0]]
                    supprimer_niveau_bdd(id_niveau, self.pseudo, self.password, window=window, resolution=resolution)

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                continuer_choix = False


# Fonction qui fait apparaître une liste des niveaux édités et qui renvoie le nom de l'image du niveau choisi

def choisir_niveau(window, temps_actuel, raccourcis, resolution):

    continuer_choix = True

    liste_etages = obtenir_liste_noms_etages()

    while continuer_choix:

        # Création du menu et affichage

        page = Page([Menu(liste_etages, 50, 50, resolution["w"]-100 if resolution["w"] >= 1024 else 924,
                          resolution["h"]-200 if resolution["h"] >= 576 else 376,
                          flags=("selection", "vertical", "defilant")),
                     Menu(("Retour", "Valider"), 0,
                          resolution["h"]-100 if resolution["h"] >= 576 else 476,
                          resolution["w"] if resolution["w"] >= 1024 else 1024, 100,
                          flags=("horizontal",))], FOND)

        sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

        # Traiter la sortie

        if isinstance(sortie, dict):

            # Bouton: Retour

            if sortie["choix"] == [1, 0]:
                continuer_choix = False

            # Bouton: Valider

            if sortie["choix"] == [1, 1] and sortie["selection"][0] is not None:
                return liste_etages[sortie["selection"][0]]

        elif sortie == 0:
            continue
        elif sortie == 1:
            exit(0)
        else:
            continuer_choix = False

    return None


# Fonction qui fait choisir au joueur un niveau edité / en ligne pour y jouer

def choisir_niveau_jouer(window, temps_actuel, raccourcis, resolution):

    continuer_choix = True
    mode_online = False

    liste_niveaux_online = list()
    liste_nom_niveaux_online = list()
    liste_nom_niveaux_edites = obtenir_liste_noms_etages()

    while continuer_choix:

        # Création du menu et affichage

        if mode_online:

            page = Page([Menu(("Niveaux édités",), 0, 0, resolution["w"] if resolution["w"] >= 1024 else 1024, 100),
                         Menu(liste_nom_niveaux_online, 50, 100,
                              resolution["w"]-100 if resolution["w"] >= 1024 else 924,
                              resolution["h"]-200 if resolution["h"] >= 576 else 376,
                              flags=("selection", "vertical", "defilant")),
                         Menu(("Retour", "Valider"), 0, resolution["h"]-100 if resolution["h"] >= 576 else 476,
                              resolution["w"] if resolution["w"] >= 1024 else 1024, 100,
                              flags=("horizontal",))], FOND)

        else:

            page = Page([Menu(("Niveaux en ligne",), 0, 0, resolution["w"] if resolution["w"] >= 1024 else 1024, 100),
                         Menu(liste_nom_niveaux_edites, 50, 100,
                              resolution["w"]-100 if resolution["w"] >= 1024 else 924,
                              resolution["h"]-200 if resolution["h"] >= 576 else 376,
                              flags=("selection", "vertical", "defilant")),
                         Menu(("Retour", "Valider"), 0, resolution["h"]-100 if resolution["h"] >= 576 else 476,
                              resolution["w"] if resolution["w"] >= 1024 else 1024, 100,
                              flags=("horizontal",))], FOND)

        sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

        # Traiter la sortie

        if isinstance(sortie, dict):

            # Bouton: Niveaux édités / Niveaux en ligne

            if sortie["choix"] == [0, 0]:
                mode_online = not mode_online

                if mode_online:
                    liste_niveaux_online = obtenir_liste_niveaux_bdd(window=window, resolution=resolution)
                    if liste_niveaux_online == "Error":
                        message_erreur = "Le serveur est déconnecté.\nVeuillez réessayer plus tard."
                        afficher_message(window, temps_actuel, raccourcis, resolution, message_erreur)
                        mode_online = False
                    else:
                        liste_nom_niveaux_online = [niveau[1] for niveau in liste_niveaux_online]

            # Bouton: Retour

            if sortie["choix"] == [2, 0]:
                continuer_choix = False

            # Bouton: Valider

            if sortie["choix"] == [2, 1] and sortie["selection"][0] is not None:
                if mode_online:
                    niveau = liste_niveaux_online[sortie["selection"][0]]
                    telecharger_niveau_bdd(niveau[0], niveau[1], window=window, resolution=resolution)
                    return niveau[1]+".png"
                else:
                    return liste_nom_niveaux_edites[sortie["selection"][0]]

        elif sortie == 0:
            continue
        elif sortie == 1:
            exit(0)
        else:
            continuer_choix = False

    return None
