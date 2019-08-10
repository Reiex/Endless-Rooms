# -*- coding:utf_8 -*

from editeur_niveaux import *
from pickle import Pickler, Unpickler


class Session:

    def __init__(self):

        self.nom = str()
        self.utiliser_sauvegarde = False
        self.tutoriel_fait = False
        self.etage = dict()
        self.joueur = dict()
        self.monstres = list()
        self.temps = list()

    # Demande le nom de session a l'utilisateur puis initialise la session

    def creer(self, window, resolution, temps_actuel, raccourcis):

        nom_deja_pris = False

        while True:

            # Creer la page du menu de création de session puis l'afficher

            if not nom_deja_pris:

                page = Page([Menu(("Pseudo:", "_", 10), 0, 0,
                                  resolution["w"] if resolution["w"] >= 1024 else 1024,
                                  resolution["h"]-100 if resolution["h"] >= 576 else 476, "input"),
                             Menu(("Retour", "Valider"), 0,
                                  resolution["h"]-100 if resolution["h"] >= 576 else 476,
                                  resolution["w"] if resolution["w"] >= 1024 else 1024, 100,
                                  flags=("horizontal",))], FOND)

            else:

                page = Page([Menu(("Le pseudo que vous avez saisi\nest déjà utilisé.",), 0, 0,
                                  resolution["w"] if resolution["w"] >= 1024 else 1024, 150, "textes"),
                             Menu(("Pseudo:", "_", 10), 0, 100,
                                  resolution["w"] if resolution["w"] >= 1024 else 1024,
                                  resolution["h"]-250 if resolution["h"] >= 576 else 326, "input"),
                             Menu(("Retour", "Valider"), 0,
                                  resolution["h"]-100 if resolution["h"] >= 576 else 476,
                                  resolution["w"] if resolution["w"] >= 1024 else 1024, 100,
                                  flags=("horizontal",))], FOND)

            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Retour

                if sortie["choix"] == [1, 0]:
                    return False

                # Bouton: Valider

                if sortie["choix"] == [2 if nom_deja_pris else 1, 1]:

                    num = 1 if nom_deja_pris else 0
                    if sortie["valeur"][num] != str() and sortie["valeur"][num] not in obtenir_liste_noms_sessions():
                        self.nom = sortie["valeur"][num]
                        return True
                    elif sortie["valeur"][num] in obtenir_liste_noms_sessions():
                        nom_deja_pris = True

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                return False

    # Affiche la liste des sessions disponnibles et fait choisir au joueur une session

    def choisir(self, window, resolution, temps_actuel, raccourcis):

        while True:

            # Créer la page liste des sessions

            page = Page([Menu(obtenir_liste_noms_sessions(), 50, 50,
                              resolution["w"]-100 if resolution["w"] >= 1024 else 924,
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
                    return False

                # Bouton: Effacer

                elif sortie["choix"] == [1, 1] and sortie["selection"][0] is not None:
                    self.nom = obtenir_liste_noms_sessions()[sortie["selection"][0]]
                    self.effacer()

                # Bouton: Valider

                elif sortie["choix"] == [1, 2] and sortie["selection"][0] is not None:
                    self.nom = obtenir_liste_noms_sessions()[sortie["selection"][0]]
                    self.recuperer()
                    return True
            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                return False

    # Inscrit la session dans un fichier qui porte le nom de la session

    def sauvegarder(self):

        with open("save/"+self.nom+".elr", "wb") as fichier:
            Pickler(fichier).dump(self)

    # Recupere la session entière a partir de self.nom

    def recuperer(self):

        with open("save/"+self.nom+".elr", "rb") as fichier:
            session_recuperee = Unpickler(fichier).load()
            for key, item in session_recuperee.__dict__.items():
                self.__setattr__(key, item)

    # Efface le fichier correspondant a {self.nom}.elr

    def effacer(self):
        try:
            remove(getcwd()+"/save/"+self.nom+".elr")
        except WindowsError:
            raise ValueError("Cette session n'existe pas")

    # A utiliser pour placer l'etage dans le session pour le sauvegarder plus tard

    def placer_etage(self, etage):

        self.utiliser_sauvegarde = True

        # N'enregistre que les objets qui peuvent être récupérés facilement

        self.etage = {}
        for key in etage.__dict__:
            if explorer(etage.__getattribute__(key)) and key != "refresh_list":
                self.etage[key] = etage.__getattribute__(key)
            elif isinstance(etage.__getattribute__(key), np.ndarray):
                self.etage[key+".ndarray"] = etage.__getattribute__(key).tolist()

        self.joueur = {}
        for key in etage.joueur.__dict__:
            if explorer(etage.joueur.__getattribute__(key)):
                self.joueur[key] = etage.joueur.__getattribute__(key)
            elif isinstance(etage.joueur.__getattribute__(key), np.ndarray):
                self.joueur[key+".ndarray"] = etage.joueur.__getattribute__(key).tolist()

        self.monstres = list()
        for i, monstre in enumerate(etage.monstres):
            self.monstres.append({})
            for key in monstre.__dict__:
                if explorer(monstre.__getattribute__(key)):
                    self.monstres[i][key] = monstre.__getattribute__(key)
                elif isinstance(monstre.__getattribute__(key), np.ndarray):
                    self.monstres[i][key+".ndarray"] = monstre.__getattribute__(key).tolist()

    # A utiliser pour modifier la variable etage avec les variables de session

    @ecran_de_chargement("Chargement")
    def recuperer_etage(self, **kwargs):

        self.utiliser_sauvegarde = False

        # Récupérer l'étage

        etage = Etage(self.etage["level"])

        for key, item in self.etage.items():
            if ".ndarray" in key:
                etage.__setattr__(key.replace(".ndarray", ""), np.array(item))
            else:
                etage.__setattr__(key, item)

        # Récupérer les données du joueur

        etage.joueur = Joueur()
        for key, item in self.joueur.items():
            if ".ndarray" in key:
                etage.joueur.__setattr__(key.replace(".ndarray", ""), np.array(item))
            else:
                etage.joueur.__setattr__(key, item)

        # Récupérer les monstres

        etage.monstres = list()
        for i, monstre in enumerate(self.monstres):
            etage.monstres.append(Monstre())
            for key, item in monstre.items():
                if ".ndarray" in key:
                    etage.monstres[i].__setattr__(key.replace(".ndarray", ""), np.array(item))
                else:
                    etage.monstres[i].__setattr__(key, item)

        # Refaire les images de l'étage car on ne peut que très difficilement les enregistrer

        etage.refresh_list = list()
        etage.fond = list()
        for y in range((etage.taille[1]*64)//TEXTURE_MAX+1):
            etage.fond.append(list())
            for x in range((etage.taille[0]*64//TEXTURE_MAX+1)):
                etage.fond[y].append(sf.RenderTexture(TEXTURE_MAX, TEXTURE_MAX))

        for y in range(etage.taille[1]):
            for x in range(etage.taille[0]):

                if (x, y) not in etage.blocs_importants["sprites_animes"]:
                    sprite = sf.Sprite(TILESET, ((etage.blocs[x, y] % 10)*64, (etage.blocs[x, y]//10)*64, 64, 64))
                else:
                    sprite = sf.Sprite(TILESET, (0, 0, 64, 64))

                sprite.position = ((x*64) % TEXTURE_MAX, (y*64) % TEXTURE_MAX)
                etage.fond[(y*64)//TEXTURE_MAX][(x*64)//TEXTURE_MAX].draw(sprite)

                etage.parametrer_shader_ombre(x, y)
                sprite.position = ((x*64) % TEXTURE_MAX, (y*64) % TEXTURE_MAX)
                etage.fond[(y*64)//TEXTURE_MAX][(x*64)//TEXTURE_MAX].draw(sprite, sf.RenderStates(shader=SHADER_OMBRE))

        for item in etage.fond:
            for chunk in item:
                chunk.display()

        return etage


class OptionsUtilisateur:

    def __init__(self):

        self.raccourcis = dict()
        self.fullscreen = False

        self.regler_raccourcis_defaut()
        self.recuperer()

    # Méthode qui réinitialiser les options

    def regler_raccourcis_defaut(self):

        self.raccourcis = {"gauche": [sf.Keyboard.Q, "Q"],
                           "droite": [sf.Keyboard.D, "D"],
                           "saut": [sf.Keyboard.SPACE, "Espace"],
                           "menu": [sf.Keyboard.ESCAPE, "Echap"],
                           "screenshot": [sf.Keyboard.F1, "F1"]}

    # Méthode qui sauvegarde les options actuelles dans user_settings.elr

    def sauvegarder(self):

        with open("user_settings.elr", "wb") as fichier:
            pickler = Pickler(fichier)
            pickler.dump(self)

    # Méthode qui récupere les options dans user_settings.elr

    def recuperer(self):

        if "user_settings.elr" in listdir(getcwd()):

            with open("user_settings.elr", "rb") as fichier:
                unpickler = Unpickler(fichier)
                options_recuperees = unpickler.load()
                for key, item in options_recuperees.__dict__.items():
                    if key == "raccourcis":
                        for raccourcis, donnees in item.items():
                            self.raccourcis[raccourcis] = donnees
                    else:
                        self.__setattr__(key, item)

    # Méthode qui ouvre un menu où l'on peut changer les options

    def modifier(self, window, temps_actuel, raccourcis, resolution):

        continuer_menu_options = True

        while continuer_menu_options:

            # Créer la page menu du programme puis l'afficher

            boutons = ("Raccourcis", "Mode fenêtré" if self.fullscreen else "Mode plein écran", "Retour")

            page = Page([Menu(boutons, 0, 0, resolution["w"] if resolution["w"] >= 1024 else 1024,
                              resolution["h"] if resolution["h"] >= 576 else 576)], FOND)
            sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

            # Traiter la sortie

            if isinstance(sortie, dict):

                # Bouton: Raccoucis

                if sortie["choix"] == [0, 0]:
                    self.modifier_raccourcis(window, temps_actuel, resolution)
                    self.sauvegarder()

                # Bouton: Mode fenêtré / Mode plein écran

                if sortie["choix"] == [0, 1]:
                    self.fullscreen = not self.fullscreen
                    if self.fullscreen:
                        resolution["w"] = sf.VideoMode.get_desktop_mode().width
                        resolution["h"] = sf.VideoMode.get_desktop_mode().height
                        window.recreate(sf.VideoMode(resolution["w"], resolution["h"], 32),
                                        "Endless-Rooms", sf.Style.FULLSCREEN)
                    else:
                        resolution["w"] = 1024
                        resolution["h"] = 576
                        window.recreate(sf.VideoMode(resolution["w"], resolution["h"], 32),
                                        "Endless-Rooms", sf.Style.DEFAULT)
                    self.sauvegarder()

                # Bouton: Retour

                elif sortie["choix"] == [0, 2]:
                    continuer_menu_options = False

            elif sortie == 0:
                continue
            elif sortie == 1:
                exit(0)
            else:
                continuer_menu_options = False

    # Méthode qui ouvre un menu qui permet de modifier les raccourcis

    def modifier_raccourcis(self, window, temps_actuel, resolution):

        # Petite fonction "creer_menu" pour ne pas avoir a recopier des bouts de code

        def creer_menu(liste_raccourcis, resolution):
            return [Menu(liste_raccourcis, 50, 50, resolution["w"]-100 if resolution["w"] >= 1024 else 924,
                         resolution["h"]-200 if resolution["h"] >= 576 else 376,
                         flags=("vertical", "defilant", "selection")),
                    Menu(("Réinitialiser", "Valider"), 0, resolution["h"]-100 if resolution["h"] > 576 else 476,
                         resolution["w"] if resolution["w"] >= 1024 else 924, 100, flags=("horizontal",))]

        # Dictionnaire qui associe a chaque touche son nom

        touches = {sf.Keyboard.A: "A", sf.Keyboard.B: "B", sf.Keyboard.C: "C", sf.Keyboard.D: "D", sf.Keyboard.E: "E",
                   sf.Keyboard.F: "F", sf.Keyboard.G: "G", sf.Keyboard.H: "H", sf.Keyboard.I: "I", sf.Keyboard.J: "J",
                   sf.Keyboard.K: "K", sf.Keyboard.L: "L", sf.Keyboard.M: "M", sf.Keyboard.N: "N", sf.Keyboard.O: "O",
                   sf.Keyboard.P: "P", sf.Keyboard.Q: "Q", sf.Keyboard.R: "R", sf.Keyboard.S: "S", sf.Keyboard.T: "T",
                   sf.Keyboard.U: "U", sf.Keyboard.V: "V", sf.Keyboard.W: "W", sf.Keyboard.X: "X", sf.Keyboard.Y: "Y",
                   sf.Keyboard.Z: "Z", sf.Keyboard.UP: "Haut", sf.Keyboard.DOWN: "Bas", sf.Keyboard.LEFT: "Gauche",
                   sf.Keyboard.RIGHT: "Droite", sf.Keyboard.ESCAPE: "Echap", sf.Keyboard.NUMPAD0: "0",
                   sf.Keyboard.NUMPAD1: "1", sf.Keyboard.NUMPAD2: "2", sf.Keyboard.NUMPAD3: "3",
                   sf.Keyboard.NUMPAD4: "4", sf.Keyboard.NUMPAD5: "5", sf.Keyboard.NUMPAD6: "6",
                   sf.Keyboard.NUMPAD7: "7", sf.Keyboard.NUMPAD8: "8", sf.Keyboard.NUMPAD9: "9", sf.Keyboard.NUM0: "à",
                   sf.Keyboard.NUM1: "&", sf.Keyboard.NUM2: "é", sf.Keyboard.NUM3: "\"", sf.Keyboard.NUM4: "'",
                   sf.Keyboard.NUM5: "(", sf.Keyboard.NUM6: "-", sf.Keyboard.NUM7: "è", sf.Keyboard.NUM8: "_",
                   sf.Keyboard.NUM9: "ç", sf.Keyboard.L_CONTROL: "L:Ctrl", sf.Keyboard.L_SHIFT: "L:Maj",
                   sf.Keyboard.F1: "F1", sf.Keyboard.F2: "F2", sf.Keyboard.F3: "F3", sf.Keyboard.F4: "F4",
                   sf.Keyboard.F5: "F5", sf.Keyboard.F6: "F6", sf.Keyboard.F7: "F7", sf.Keyboard.F8: "F8",
                   sf.Keyboard.F9: "F9", sf.Keyboard.F10: "F10", sf.Keyboard.F11: "F11", sf.Keyboard.F12: "F12"}

        # Faire la liste des menus

        liste_raccourcis = [key+" - "+item[1] for key, item in self.raccourcis.items()]

        liste_menus = creer_menu(liste_raccourcis, resolution)

        # Variables à initialiser

        choix = -1
        selection = str()
        position_souris = [0, 0]
        window.view.reset((0, 0, resolution["w"], resolution["h"]))
        fond = sf.Sprite(sf.Texture.from_image(FOND))
        fond.position = (0, 0)
        tempo = 0
        continuer_menu = True

        while continuer_menu:

            tempo = (tempo+1) % 24

            # RAFRAICHIR L'IMAGE

            window.display()
            window.clear(sf.Color(0, 0, 0))
            window.draw(fond)
            gerer_fps(temps_actuel)

            # GESTION DES EVENEMENTS

            for event in window.events:

                # Evenements universels

                if isinstance(event, sf.ResizeEvent):
                    resolution["w"], resolution["h"] = event.size.x, event.size.y
                    window.view.reset((0, 0, resolution["w"], resolution["h"]))
                    liste_menus = creer_menu(liste_raccourcis, resolution)
                if isinstance(event, sf.CloseEvent):
                    exit(0)

                # Clique

                if isinstance(event, sf.MouseButtonEvent):
                    if event.button == sf.Mouse.LEFT and event.released:
                        for menu in liste_menus:
                            for b, bouton in enumerate(menu.boutons):
                                if bouton.x < position_souris[0] < bouton.x+bouton.w and \
                                   bouton.y < position_souris[1] < bouton.y+bouton.h:
                                    if "selection" in menu.flags or menu.type == "saisies":
                                        selection = liste_raccourcis[b].split(" - ")[0]
                                        for autre_bouton in menu.boutons:
                                            if autre_bouton is bouton:
                                                bouton.data["selection"] = not bouton.data["selection"]
                                            else:
                                                autre_bouton.data["selection"] = False
                                    else:
                                        choix = b

                # Entrée clavier

                if isinstance(event, sf.KeyEvent):
                    if selection != str():
                        if event.code in touches.keys():
                            self.raccourcis[selection] = [event.code, touches[event.code]]
                            liste_raccourcis = [key+" - "+item[1] for key, item in self.raccourcis.items()]
                            liste_menus = creer_menu(liste_raccourcis, resolution)
                        selection = str()

                # Molette

                if isinstance(event, sf.MouseWheelEvent):
                    for menu in liste_menus:
                        if "defilant" in menu.flags:
                            if len(menu.boutons) > 0:
                                mouvement = ("horizontal" in menu.flags and
                                             ((event.delta < 0 and menu.boutons[len(menu.boutons)-1].x+event.delta*32 > menu.x) or
                                              (event.delta > 0 and menu.boutons[0].x+menu.boutons[0].w+event.delta*32 < menu.x+menu.w))) or \
                                            ("horizontal" not in menu.flags and
                                             ((event.delta < 0 and menu.boutons[len(menu.boutons)-1].y+event.delta*32 > menu.y) or
                                              (event.delta > 0 and menu.boutons[0].y+menu.boutons[0].h+event.delta*32 < menu.y+menu.h)))
                                if "defilant" in menu.flags and mouvement:
                                    for bouton in menu.boutons:
                                        if "horizontal" in menu.flags:
                                            bouton.x += event.delta*32
                                        else:
                                            bouton.y += event.delta*32

            position_souris = sf.Mouse.get_position(window)

            # AFFICHAGE

            for m, menu in enumerate(liste_menus):

                # Afficher le fond du menu

                if menu.fond is not None:
                    window.draw(menu.fond)

                elif menu.type == "normal":

                    # Créer et afficher le fond du menu défilant

                    if "defilant" in menu.flags:
                        contour = sf.RectangleShape()
                        contour.size = (menu.w, menu.h)
                        contour.outline_color = sf.Color(0, 0, 0)
                        contour.outline_thickness = 2
                        contour.position = (menu.x, menu.y)
                        window.draw(contour)

                    # Afficher les boutons du menu

                    for b, bouton in enumerate(menu.boutons):

                        # Si c'est le menu défilant

                        if "defilant" in menu.flags:

                            coordonnees_sprite = {"x": bouton.x, "y": bouton.y, "cadre": [0, 0, bouton.w, bouton.h]}

                            if bouton.x < menu.x < bouton.x+bouton.w:
                                coordonnees_sprite["cadre"][0] = menu.x-bouton.x
                                coordonnees_sprite["cadre"][2] = bouton.x+bouton.w-menu.x
                                coordonnees_sprite["x"] = menu.x
                            if bouton.x < menu.x+menu.w < bouton.x+bouton.w:
                                coordonnees_sprite["cadre"][2] = menu.x+menu.w-bouton.x
                            if bouton.y < menu.y < bouton.y+bouton.h:
                                coordonnees_sprite["cadre"][1] = menu.y-bouton.y
                                coordonnees_sprite["cadre"][3] = bouton.y+bouton.h-menu.y
                                coordonnees_sprite["y"] = menu.y
                            if bouton.y < menu.y+menu.h < bouton.y+bouton.h:
                                coordonnees_sprite["cadre"][3] = menu.y+menu.h-bouton.y

                            if bouton.x < position_souris[0] < bouton.x+bouton.w and \
                               bouton.y < position_souris[1] < bouton.y+bouton.h:
                                if "selection" in menu.flags:
                                    if bouton.data["selection"]:
                                        sprite = sf.Sprite(bouton.images["selection"], coordonnees_sprite["cadre"])
                                    else:
                                        sprite = sf.Sprite(bouton.images["passage"], coordonnees_sprite["cadre"])
                                else:
                                    sprite = sf.Sprite(bouton.images["passage"], coordonnees_sprite["cadre"])
                            else:
                                if "selection" in menu.flags:
                                    if bouton.data["selection"]:
                                        sprite = sf.Sprite(bouton.images["selection"], coordonnees_sprite["cadre"])
                                    else:
                                        sprite = sf.Sprite(bouton.images["normal"], coordonnees_sprite["cadre"])
                                else:
                                    sprite = sf.Sprite(bouton.images["normal"], coordonnees_sprite["cadre"])

                            if bouton.x+bouton.w > menu.x and bouton.x < menu.x+menu.w and \
                               bouton.y+bouton.h > menu.y and bouton.y < menu.y+menu.h:
                                sprite.position = (coordonnees_sprite["x"], coordonnees_sprite["y"])
                                window.draw(sprite)

                        # Sinon

                        else:

                            if bouton.x < position_souris[0] < bouton.x+bouton.w and \
                               bouton.y < position_souris[1] < bouton.y+bouton.h:
                                if "selection" in menu.flags:
                                    if bouton.data["selection"]:
                                        sprite = sf.Sprite(bouton.images["selection"])
                                    else:
                                        sprite = sf.Sprite(bouton.images["passage"])
                                else:
                                    sprite = sf.Sprite(bouton.images["passage"])
                            else:
                                if "selection" in menu.flags:
                                    if bouton.data["selection"]:
                                        sprite = sf.Sprite(bouton.images["selection"])
                                    else:
                                        sprite = sf.Sprite(bouton.images["normal"])
                                else:
                                    sprite = sf.Sprite(bouton.images["normal"])

                            sprite.position = (bouton.x, bouton.y)
                            window.draw(sprite)

            if choix != -1:

                # Bouton: Réinitialiser

                if choix == 0:
                    self.regler_raccourcis_defaut()
                    liste_raccourcis = [key+" - "+item[1] for key, item in self.raccourcis.items()]
                    liste_menus = creer_menu(liste_raccourcis, resolution)

                # Bouton: Valider

                if choix == 1:
                    continuer_menu = False

                choix = -1
