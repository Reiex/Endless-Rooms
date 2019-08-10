# -*- coding:utf-8 -*

from fonctions_recurrentes import *
from re import search

FOND = sf.Image.from_file("images/fond.png")
ASCII = sf.Image.from_file("images/ascii.png")
ASCII.create_mask_from_color(sf.Color(255, 255, 255))
ASCII_PASSAGE = sf.Image.from_file("images/ascii_passage.png")
ASCII_PASSAGE.create_mask_from_color(sf.Color(255, 255, 255))
ASCII_SELECTION = sf.Image.from_file("images/ascii_selection.png")
ASCII_SELECTION.create_mask_from_color(sf.Color(255, 255, 255))
ASCII_MINI = sf.Image.from_file("images/ascii_mini.png")
INTERFACE_IMAGE = sf.Image.from_file("images/interface.png")
INTERFACE_IMAGE.create_mask_from_color(sf.Color(255, 255, 255))


class Page:

    def __init__(self, menus, fond=FOND):

        self.menus = list(menus)
        self.fond = sf.Texture.from_image(fond)

    # Affiche et renvoie le choix du menu

    def afficher(self, window, temps_actuel, raccourcis, resolution):

        position_souris = [0, 0]
        window.view.reset((0, 0, resolution["w"], resolution["h"]))
        choix = list()
        fond = sf.Sprite(self.fond)
        fond.position = (0, 0)
        tempo = 0

        while not choix:

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
                    return 0
                if isinstance(event, sf.CloseEvent):
                    return 1
                if isinstance(event, sf.KeyEvent):
                    if event.code == raccourcis["menu"][0] and event.released:
                        return None

                # Clique

                if isinstance(event, sf.MouseButtonEvent):
                    if event.button == sf.Mouse.LEFT and event.released:
                        for m, menu in enumerate(self.menus):
                            if menu.type != "input":
                                for b, bouton in enumerate(menu.boutons):
                                    if bouton.x < position_souris[0] < bouton.x+bouton.w and \
                                       bouton.y < position_souris[1] < bouton.y+bouton.h:
                                        if "selection" in menu.flags or menu.type == "saisies":
                                            for autre_bouton in menu.boutons:
                                                if autre_bouton is bouton:
                                                    bouton.data["selection"] = not bouton.data["selection"]
                                                else:
                                                    autre_bouton.data["selection"] = False
                                        else:
                                            choix = [m, b]

                # Entrée clavier

                if isinstance(event, sf.TextEvent):
                    for menu in self.menus:
                        if menu.type == "input":
                            if search(CARACTERES_AUTORISES, chr(event.unicode)) and \
                               len(menu.boutons.data["valeur"]) < menu.boutons.data["maxlength"]:
                                menu.boutons.data["valeur"] += chr(event.unicode)
                            elif ord(chr(event.unicode)) == 8:
                                menu.boutons.data["valeur"] = menu.boutons.data["valeur"][:-1]
                        elif menu.type == "saisies":
                            for bouton in menu.boutons:
                                if bouton.data["selection"]:
                                    if search(CARACTERES_AUTORISES, chr(event.unicode)) and \
                                       len(bouton.data["valeur"]) < bouton.data["maxlength"]:
                                        bouton.data["valeur"] += chr(event.unicode)
                                    elif ord(chr(event.unicode)) == 8:
                                        bouton.data["valeur"] = bouton.data["valeur"][:-1]

                # Molette

                if isinstance(event, sf.MouseWheelEvent):
                    for menu in self.menus:
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

            for m, menu in enumerate(self.menus):

                # Afficher le fond du menu

                if menu.fond is not None:
                    window.draw(menu.fond)

                # Si c'est un input

                if menu.type == "input":

                    # Afficher le titre de l'input

                    menu.boutons.x = menu.x+(menu.w-menu.boutons.w-32*len(menu.boutons.data["valeur"]))//2

                    sprite = sf.Sprite(menu.boutons.images["avant"])
                    sprite.position = (menu.boutons.x,
                                       menu.boutons.y+(menu.boutons.h-menu.boutons.images["avant"].height)//2)
                    window.draw(sprite)

                    # Afficher le contenu de l'input

                    if menu.boutons.data["valeur"] != "":
                        image = sf.Image.create(32*len(menu.boutons.data["valeur"]), 64, sf.Color(255, 255, 255))
                        for i, char in enumerate(menu.boutons.data["valeur"]):
                            image.blit(ASCII, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
                        image.create_mask_from_color(sf.Color(255, 255, 255))
                        sprite = sf.Sprite(sf.Texture.from_image(image))
                        sprite.position = (menu.boutons.x+menu.boutons.images["avant"].width,
                                           menu.boutons.y+(menu.boutons.h-64)//2)
                        window.draw(sprite)

                    # Afficher le curseur

                    if tempo < 12:
                        sprite = sf.Sprite(menu.boutons.images["apres"])
                        sprite.position = (menu.boutons.x+menu.boutons.images["avant"].width+32*len(menu.boutons.data["valeur"]),
                                           menu.boutons.y+(menu.boutons.h-menu.boutons.images["apres"].height)//2)
                        window.draw(sprite)

                # Si c'est une liste de saisies

                elif menu.type == "saisies":

                    for b, bouton in enumerate(menu.boutons):

                        # Afficher le champ de saisie et le curseur

                        if bouton.data["selection"]:
                            if tempo < 12 and len(bouton.data["valeur"]) < bouton.data["maxlength"]:
                                sprite = sf.Sprite(bouton.images["curseur"])
                                sprite.position = (bouton.x+4+len(bouton.data["valeur"])*32+(bouton.w-bouton.data["maxlength"]*32)//2, bouton.y+68)
                                window.draw(sprite)
                            sprite = sf.Sprite(bouton.images["selection"])
                        else:
                            sprite = sf.Sprite(bouton.images["normal"])

                        sprite.position = (bouton.x, bouton.y)
                        window.draw(sprite)

                        # Afficher le texte dans le champ de saisie

                        if bouton.data["valeur"] != "":

                            image = sf.Image.create(32*len(bouton.data["valeur"]), 64, sf.Color(255, 255, 255))
                            for i, char in enumerate(bouton.data["valeur"]):
                                image.blit(ASCII, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
                            image.create_mask_from_color(sf.Color(255, 255, 255))
                            sprite = sf.Sprite(sf.Texture.from_image(image))
                            sprite.position = (bouton.x+(bouton.w-bouton.data["maxlength"]*32)//2, bouton.y+68)
                            window.draw(sprite)

                # Si c'est un texte

                elif menu.type == "textes":

                    for bouton in menu.boutons:
                        sprite = sf.Sprite(bouton.images["normal"])
                        sprite.position = (bouton.x, bouton.y)
                        window.draw(sprite)

                # Si c'est un menu normal

                elif menu.type == "normal":

                    # Créer et afficher le fond si c'est un menu defilant

                    if "defilant" in menu.flags:
                        contour = sf.RectangleShape()
                        contour.size = (menu.w, menu.h)
                        contour.outline_color = sf.Color(0, 0, 0)
                        contour.outline_thickness = 2
                        contour.position = (menu.x, menu.y)
                        window.draw(contour)

                    # Afficher les boutons du menu

                    for b, bouton in enumerate(menu.boutons):

                        # Si c'est un menu défilant

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

        # CREER LA SORTIE

        sortie = {"choix": choix, "valeur": [], "selection": []}
        for m, menu in enumerate(self.menus):
            sortie["valeur"].append(0)
            if menu.type == "input":
                sortie["valeur"][m] = menu.boutons.data["valeur"]
            elif menu.type == "saisies":
                liste_valeurs = list()
                for bouton in menu.boutons:
                    liste_valeurs.append(bouton.data["valeur"])
                sortie["valeur"][m] = liste_valeurs
            elif "selection" in menu.flags:
                selected = False
                for b, bouton in enumerate(menu.boutons):
                    if bouton.data["selection"]:
                        selected = True
                        sortie["selection"].append(b)
                if not selected:
                    sortie["selection"].append(None)

        return sortie


class Menu:

    def __init__(self, args, x, y, w, h, type_menu="normal", flags=("vertical",), fond=None):

        self.boutons = list()
        self.fond = fond
        self.type = type_menu
        self.flags = flags
        self.creer_menu(args, x, y, w, h)
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    # Méthode qui appelle la bonne méthode en fonction du flag donné, sert uniquement à ne pas encombrer __init__

    def creer_menu(self, args, x, y, w, h):

        if isinstance(self.flags, list) or isinstance(self.flags, tuple):
            if self.type == "normal":
                self.creer_menu_normal(args, x, y, w, h)
            elif self.type == "input":
                self.creer_menu_input(args, x, y, w, h)
            elif self.type == "saisies":
                self.creer_menu_saisies(args, x, y, w, h)
            elif self.type == "textes":
                self.creer_texte(args, x, y, w, h)

        else:
            raise ValueError("Les flags doivent être dans une liste ou un tuple")

    # Methodes a appeler en fonction du type de menu

    def creer_menu_normal(self, args, x, y, w, h):

        if not isinstance(args, tuple) and not isinstance(args, list):
            raise ValueError("Les arguments passés à la création du menu ne sont pas reconnus")

        # Création des coordonnées du fond

        if self.fond is not None:
            self.fond.position = (x, y)

        # Création de tout les boutons

        taille = [0, 0]
        for item in args:

            bouton = Bouton()

            # OBTENIR LES IMAGES

            # Si l'argument est un tuple ou une liste de sf.Texture

            if (isinstance(item, tuple) or isinstance(item, list)) and isinstance(item[0], sf.Texture):
                tailles_images = list()
                bouton.images["normal"] = item[0]
                tailles_images.append([item[0].width, item[0].height])
                try:
                    bouton.images["passage"] = item[1]
                    tailles_images.append([item[1].width, item[1].height])
                except IndexError:
                    bouton.images["passage"] = bouton.images["normal"]
                if "selection" in self.flags:
                    bouton.data["selection"] = False
                    try:
                        bouton.images["selection"] = item[2]
                        tailles_images.append([item[2].width, item[2].height])
                    except IndexError:
                        bouton.images["selection"] = bouton.images["passage"]

                bouton.w = sorted(tailles_images, key=lambda objet: objet[0])[-1]
                bouton.h = sorted(tailles_images, key=lambda objet: objet[1])[-1]

            # Si l'argument est une chaine de caracteres

            elif isinstance(item, str):
                bouton.w, bouton.h = len(item)*32, 64
                normal = sf.Image.create(bouton.w, bouton.h, sf.Color(255, 255, 255))
                passage = sf.Image.create(bouton.w, bouton.h, sf.Color(255, 255, 255))
                for i, char in enumerate(item):
                    normal.blit(ASCII, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
                    passage.blit(ASCII_PASSAGE, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
                normal.create_mask_from_color(sf.Color(255, 255, 255))
                passage.create_mask_from_color(sf.Color(255, 255, 255))
                bouton.images["normal"] = sf.Texture.from_image(normal)
                bouton.images["passage"] = sf.Texture.from_image(passage)
                if "selection" in self.flags:
                    bouton.data["selection"] = False
                    selection = sf.Image.create(bouton.w, bouton.h, sf.Color(255, 255, 255))
                    for i, char in enumerate(item):
                        selection.blit(ASCII_SELECTION, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
                    selection.create_mask_from_color(sf.Color(255, 255, 255))
                    bouton.images["selection"] = sf.Texture.from_image(selection)

            # Si l'argument n'est pas reconnu

            else:
                raise ValueError(item, " dans ", args, " n'est pas une valeur valide")

            # Ajouter la taille du bouton a la taille minimale du menu si c'est un menu non-défilant

            if "defilant" not in self.flags:
                if "horizontal" in self.flags:
                    taille[0] += bouton.w
                    if bouton.h > taille[1]:
                        taille[1] = bouton.h
                else:
                    taille[1] += bouton.h
                    if bouton.w > taille[0]:
                        taille[0] = bouton.w

            self.boutons.append(bouton)

        # CALCULER LES COORDONNEES

        # Si le menu est défilant

        curseur = 64
        if "defilant" in self.flags:

            for i, bouton in enumerate(self.boutons):

                if "horizontal" in self.flags:
                    bouton.y = y+(h-bouton.h)//2
                    bouton.x = x+curseur
                    curseur += bouton.w+128
                else:
                    bouton.x = x+(w-bouton.w)//2
                    bouton.y = y+16+128*i

        # Si le menu n'est pas défilant

        else:

            # Lever une exception si le menu est trop grand

            if taille[0] > w or taille[1] > h:
                raise ValueError("Le menu est trop grand pour les coordonnees fournies")

            # Calculer l'espace entre deux boutons

            if "horizontal" in self.flags:
                espace = (w-taille[0])//(len(args)+1)
            else:
                espace = (h-taille[1])//(len(args)+1)

            # OBTENIR LES COORDONNEES DE CHAQUE BOUTON

            curseur = 0

            for i, bouton in enumerate(self.boutons):

                if "horizontal" in self.flags:
                    curseur += espace
                    bouton.x = x+curseur
                    bouton.y = (h-bouton.h)//2+y
                    curseur += bouton.w
                else:
                    curseur += espace
                    bouton.y = y+curseur
                    bouton.x = (w-bouton.w)//2+x
                    curseur += bouton.h

    def creer_menu_input(self, args, x, y, w, h):

        if not(isinstance(args, list) or isinstance(args, tuple)):
            raise ValueError("Les arguments passés à la création du menu input ne sont pas les bons.")

        if self.fond is not None:
            self.fond.position = (x, y)

        bouton = Bouton()

        # OBTENIR L'IMAGE A METTRE DEVANT L'ENTREE DE TEXTE

        # Si une chaine de caractère est donnée

        if isinstance(args[0], str) and args[0] != str():
            image = sf.Image.create(32*len(args[0]), 64, sf.Color(255, 255, 255))
            for i, char in enumerate(args[0]):
                image.blit(ASCII, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
            image.create_mask_from_color(sf.Color(255, 255, 255))
            bouton.images["avant"] = sf.Texture.from_image(image)
            bouton.h = 64
            bouton.w = 32*len(args[0])

        # Si une texture est donnée

        elif isinstance(args[0], sf.Texture):
            bouton.images["avant"] = args[0]
            bouton.h = args[0].height if args[0].height > 64 else 64
            bouton.w = args[0].width

        else:
            raise ValueError(args[0], " n'est pas un argument valide pour l'image/le texte a mettre devant l'input")

        # OBTENIR L'IMAGE DU CURSEUR A METTRE A LA FIN DE L'ENTREE DE TEXTE

        # Si une chaine de caractère est donnée

        if isinstance(args[1], str):
            image = sf.Image.create(32*len(args[1]), 64, sf.Color(255, 255, 255))
            for i, char in enumerate(args[1]):
                image.blit(ASCII, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
            image.create_mask_from_color(sf.Color(255, 255, 255))
            bouton.images["apres"] = sf.Texture.from_image(image)
            bouton.w += 32*len(args[1])

        # Si une texture est donnée

        elif isinstance(args[1], sf.Texture):
            bouton.images["apres"] = args[1]
            bouton.h = args[1].height if args[1].height > bouton.h else bouton.h
            bouton.w += args[1].width

        else:
            raise ValueError(args[1], " n'est pas un argument valide")

        # Obtenir la longueur maximale de l'input

        try:
            bouton.data["maxlength"] = args[2]
        except IndexError:
            bouton.data["maxlength"] = 15

        if bouton.w + bouton.data["maxlength"]*32 > w:
            raise ValueError("L'input est trop long")

        # Obtenir la valeur prédéfinie de l'input

        try:
            bouton.data["valeur"] = args[3]
        except IndexError:
            bouton.data["valeur"] = ""

        bouton.y = y+(h-bouton.h)//2

        self.boutons = bouton

    def creer_menu_saisies(self, args, x, y, w, h):

        if self.fond is not None:
            self.fond.position = (x, y)

        if not isinstance(args, tuple) and not isinstance(args, list):
            raise ValueError("Les arguments passés à la création du menu textarea ne sont pas reconnus")

        taille_mini = [0, 0]

        for item in args:

            bouton = Bouton()

            # Obtenir les images du titre de l'input

            if isinstance(item[0], str) and item[0] != str():
                titre = sf.Image.create(32*len(item[0]), 64, sf.Color(255, 255, 255))
                titre_selection = sf.Image.create(32*len(item[0]), 64, sf.Color(255, 255, 255))
                for i, char in enumerate(item[0]):
                    titre.blit(ASCII, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
                    titre_selection.blit(ASCII_SELECTION, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
                titre.create_mask_from_color(sf.Color(255, 255, 255))
                titre_selection.create_mask_from_color(sf.Color(255, 255, 255))
                bouton.w = 32*len(item[0])
            else:
                raise ValueError(item[0], " n'est pas un argument valide pour le texte a mettre devant l'input")

            # Obtenir le curseur de l'input

            if isinstance(item[1], str) and item[1] != str():
                curseur = sf.Image.create(32*len(item[1]), 64, sf.Color(255, 255, 255))
                for i, char in enumerate(item[1]):
                    curseur.blit(ASCII, (i*32, 0), ((ord(char) % 10)*32, (ord(char)//10)*64, 32, 64))
                curseur.create_mask_from_color(sf.Color(255, 255, 255))
                bouton.images["curseur"] = sf.Texture.from_image(curseur)
            else:
                raise ValueError(item[1], " n'est pas un argument valide pour le curseur de l'input")

            # Obtenir la taille maximale de l'input

            try:
                bouton.data["maxlength"] = item[2]
            except IndexError:
                bouton.data["maxlength"] = 15

            # Obtenir la valeur de l'input

            try:
                bouton.data["valeur"] = item[3]
            except IndexError:
                bouton.data["valeur"] = str()

            # Initialiser la selection de l'input

            bouton.data["selection"] = False

            # Créer l'image de fond puis les images définitives

            saisie = sf.Image.create(32*bouton.data["maxlength"]+8, 72, sf.Color(255, 255, 0))
            saisie.blit(sf.Image.create(32*bouton.data["maxlength"]+4, 68, sf.Color(255, 255, 255)), (2, 2))
            saisie.create_mask_from_color(sf.Color(255, 255, 255))
            saisie_selection = sf.Image.create(32*bouton.data["maxlength"]+8, 72, sf.Color(63, 72, 204))
            saisie_selection.blit(sf.Image.create(32*bouton.data["maxlength"]+4, 68, sf.Color(255, 255, 255)), (2, 2))
            saisie_selection.create_mask_from_color(sf.Color(255, 255, 255))

            bouton.w = 32*bouton.data["maxlength"]+8 if 32*bouton.data["maxlength"]+8 > bouton.w else bouton.w
            bouton.h = 136

            image = sf.Image.create(bouton.w, bouton.h, sf.Color(255, 255, 255))
            image.blit(titre, ((image.width-titre.width)//2, 0))
            image.blit(saisie, ((image.width-saisie.width)//2, 64))
            image.create_mask_from_color(sf.Color(255, 255, 255))
            bouton.images["normal"] = sf.Texture.from_image(image)
            image_selection = sf.Image.create(bouton.w, bouton.h, sf.Color(255, 255, 255))
            image_selection.blit(titre_selection, ((image.width-titre_selection.width)//2, 0))
            image_selection.blit(saisie_selection, ((image.width-saisie_selection.width)//2, 64))
            image_selection.create_mask_from_color(sf.Color(255, 255, 255))
            bouton.images["selection"] = sf.Texture.from_image(image_selection)

            # Ajouter la taille du bouton a la taille minimale du menu

            if "horizontal" in self.flags:
                taille_mini[0] += bouton.w
                taille_mini[1] = bouton.h if bouton.h > taille_mini[1] else taille_mini[1]
            else:
                taille_mini[0] = bouton.w if bouton.w > taille_mini[0] else taille_mini[0]
                taille_mini[1] += bouton.h

            self.boutons.append(bouton)

        # Obtenir les coordonnées de chaque bouton

        if taille_mini[0] > w or taille_mini[1] > h:
            raise ValueError("Le menu est trop petit pour accueillir toute les saisies")

        position_curseur = 0
        for bouton in self.boutons:
            if "horizontal" in self.flags:
                position_curseur += (w-taille_mini[0])//(len(self.boutons)+1)
                bouton.x = x+position_curseur
                bouton.y = y+(h-bouton.h)//2
                position_curseur += bouton.w
            else:
                position_curseur += (h-taille_mini[1])//(len(self.boutons)+1)
                bouton.y = y+position_curseur
                bouton.x = x+(w-bouton.w)//2
                position_curseur += bouton.h

        self.boutons[0].data["selection"] = True

    def creer_texte(self, args, x, y, w, h):

        if self.fond is not None:
            self.fond.position = (x, y)

        if not isinstance(args, tuple) and not isinstance(args, list):
            raise ValueError("Les arguments passés à la création du texte ne sont pas reconnus")

        taille_mini = [0, 0]
        for chaine in args:

            message = chaine.split("\n")
            bouton = Bouton()
            bouton.w = len(sorted(message, key=lambda line: -len(line))[0])*32
            bouton.h = len(message)*64
            normal = sf.Image.create(bouton.w, bouton.h, sf.Color(255, 255, 255))
            for y, ligne in enumerate(message):
                for x, c in enumerate(ligne):
                    normal.blit(ASCII, (x*32+(bouton.w-len(ligne)*32)//2, y*64),
                                ((ord(c) % 10)*32, (ord(c)//10)*64, 32, 64))
            normal.create_mask_from_color(sf.Color(255, 255, 255))
            bouton.images["normal"] = sf.Texture.from_image(normal)

            if "horizontal" in self.flags:
                taille_mini[0] += bouton.w
                taille_mini[1] = bouton.h if bouton.h > taille_mini[1] else taille_mini[1]
            else:
                taille_mini[1] += bouton.h
                taille_mini[0] = bouton.w if bouton.w > taille_mini[0] else taille_mini[0]

            self.boutons.append(bouton)

        if taille_mini[0] > w or taille_mini[1] > h:
            raise ValueError("Le texte est trop grand pour les coordonnees fournies")

        curseur = x if "horizontal" in self.flags else y
        for bouton in self.boutons:
            if "horizontal" in self.flags:
                curseur += (w-taille_mini[0])//(len(self.boutons)+1)
                bouton.x = curseur
                bouton.y = y+(h-bouton.h)//2
                curseur += bouton.w
            else:
                curseur += (h-taille_mini[1])//(len(self.boutons)+1)
                bouton.y = curseur
                bouton.x = x+(w-bouton.w)//2
                curseur += bouton.h


class Bouton:

    def __init__(self):

        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.images = {}
        self.data = {}


class Fenetre:

    def __init__(self, message, x=0, y=0):

        self.x = x
        self.y = y
        self.w = 0
        self.h = 0
        self.image = sf.Texture.create(1, 1)
        self.message = message
        self.creer(message)

    def creer(self, message):

        # Anticiper les possibles erreurs

        if message is None:
            return None
        elif not isinstance(message, str):
            raise ValueError("Le message à afficher doit être une chaine de caractères. Message donné:", message)

        # Obtenir la taille de la fenêtre

        chaine = message.split("\n")
        self.w = len(sorted(chaine, key=lambda foo: len(foo))[-1])*12+8
        self.h = len(chaine)*24+20

        # Créer l'image de fond

        image = sf.Image.create(self.w, self.h, sf.Color(0, 0, 0))
        fond = sf.Image.create(self.w-4, self.h-4, sf.Color(150, 150, 150))
        image.blit(fond, (2, 2))
        image.blit(INTERFACE_IMAGE, (self.w-12, 0), (0, 96, 12, 12))

        # Ajouter les caractères

        for y, ligne in enumerate(chaine):
            for x, char in enumerate(ligne):
                image.blit(ASCII_MINI, ((self.w-len(ligne)*12)//2+x*12, 16+y*24),
                           ((ord(char) % 10)*12, (ord(char)//10)*24, 12, 24))

        self.image = sf.Texture.from_image(image)


# Fonction à ouvrir dans un thread qui affiche un ecran de chargement tant que data_thread["continuer"] vaut True

def fonction_ecran_de_chargement(window, resolution, data_thread, message_a_afficher="Chargement"):

    # Créé la texture du mot "Chargement", du fond, et d'un point

    longueur = 32*len(message_a_afficher)
    message = sf.Image.create(longueur, 64, sf.Color(255, 255, 255))
    for i, c in enumerate(message_a_afficher):
        message.blit(ASCII, (i*32, 0), ((ord(c) % 10)*32, (ord(c)//10)*64, 32, 64))
    message.create_mask_from_color(sf.Color(255, 255, 255))
    message = sf.Texture.from_image(message)
    sprite_message = sf.Sprite(message)
    point = sf.Texture.from_image(ASCII, (192, 256, 32, 64))
    sprite_point = sf.Sprite(point)
    fond = sf.Sprite(sf.Texture.from_image(FOND))

    # Initialise quelques variables puis démarre la boucle de l'écran de chargement

    tempo = 0
    temps_actuel = sf.Clock()

    while data_thread["continuer"]:

        # Mettre a jour l'ecran

        window.display()
        gerer_fps(temps_actuel)

        # Gestion des evenements

        for event in window.events:
            if isinstance(event, sf.ResizeEvent):
                resolution["w"], resolution["h"] = event.size.x, event.size.y
                window.view.reset((0, 0, resolution["w"], resolution["h"]))

        # Afficher le fond avec le mot "chargement" et des points qui bougent

        tempo = (tempo+1) % 24
        window.clear(sf.Color(0, 0, 0))
        window.draw(fond)
        sprite_message.position = ((resolution["w"]-longueur-96)//2, resolution["h"]-100)
        window.draw(sprite_message)
        for i in range(tempo//6):
            sprite_point.position = ((resolution["w"]-longueur-96)//2+longueur+32*i, resolution["h"]-100)
            window.draw(sprite_point)

    window.active = False


# Fonction qui ouvre une fenêtre dans laquelle est affichée le message et avec un bouton "Continuer" qui arrête le menu

def afficher_message(window, temps_actuel, raccourcis, resolution, message):

    continuer_message = True

    while continuer_message:

        # Créer la page menu du programme puis l'afficher

        page = Page([Menu((message,), 0, 0, resolution["w"] if resolution["w"] >= 1024 else 1024,
                          resolution["h"]-100 if resolution["h"] >= 576 else 476, "textes"),
                     Menu(("Continuer",), 0, resolution["h"]-100 if resolution["h"] >= 576 else 476,
                          resolution["w"] if resolution["w"] >= 1024 else 1024, 100)], FOND)
        sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

        # Traiter la sortie

        if isinstance(sortie, dict):

            # Bouton: Continuer

            if sortie["choix"] == [1, 0]:
                continuer_message = False

        elif sortie == 0:
            continue
        elif sortie == 1:
            exit(0)
        else:
            continue


# Décorateur à placer devant chaque fonction qui a besoin d'un ecran de chargement
# Toutes les fonctions avec ce décorateur doivent accueillir **kwargs et être appelées avec window et resolution

def ecran_de_chargement(message):

    def decorateur(fonction):

        def fonction_avec_ecran_chargement(*args, **kwargs):

            # Ouvrir un thread dans lequel on affiche l'ecran de chargement

            data_thread = {"continuer": True}
            kwargs["window"].active = False
            chargement = sf.Thread(fonction_ecran_de_chargement, kwargs["window"], kwargs["resolution"], data_thread, message)
            chargement.launch()

            # Parallèlement, faire charger l'étage dans le thread principal

            valeur_renvoyee = fonction(*args, **kwargs)

            # Arrêter l'ecran de chargement

            data_thread["continuer"] = False
            chargement.wait()
            chargement.terminate()

            return valeur_renvoyee

        return fonction_avec_ecran_chargement

    return decorateur
