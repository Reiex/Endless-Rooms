# -*- coding:utf_8 -*

from session import *
import pygame
import pygame._view

# Charger les options de l'utilisateur s'il en a, sinon en créer des nouvelles

options_utilisateur = OptionsUtilisateur()
raccourcis = options_utilisateur.raccourcis

# Ouvrir une fenêtre

if options_utilisateur.fullscreen:
    resolution = {"w": sf.VideoMode.get_desktop_mode().width, "h": sf.VideoMode.get_desktop_mode().height}
    window = sf.RenderWindow(sf.VideoMode(resolution["w"], resolution["h"], 32), "Endless-rooms", sf.Style.FULLSCREEN)
else:
    resolution = {"w": 1024, "h": 576}
    window = sf.RenderWindow(sf.VideoMode(resolution["w"], resolution["h"], 32), "Endless-rooms", sf.Style.DEFAULT)

# Création des dossiers /save, /edit et /screenshots s'ils n'existent pas afin d'éviter de potentiels bugs

if "save" not in listdir(getcwd()):
    mkdir(getcwd()+"/save")

if "edit" not in listdir(getcwd()):
    mkdir(getcwd()+"/edit")

if "screenshots" not in listdir(getcwd()):
    mkdir(getcwd()+"/screenshots")

# Initialisation de variables

temps_actuel = sf.Clock()
continuer_menu_jeu = True
continuer_menu_session = False
continuer_jeu = False
continuer_niveau = False
niveau_actuel = int()
window.view = sf.View()

# ----------------------------------------------------------------------------------------------------------------------
# BOUCLE DU PROGRAMME
# ----------------------------------------------------------------------------------------------------------------------

while continuer_menu_jeu:

    # Créer la page menu du programme puis l'afficher

    page = Page([Menu(("Creer une session", "Choisir une session", "Editeur de niveaux", "Options", "Quitter le jeu"),
                      0, 0, resolution["w"] if resolution["w"] >= 1024 else 1024,
                      resolution["h"] if resolution["h"] >= 576 else 576)], FOND)
    sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

    # Traiter la sortie

    if isinstance(sortie, dict):

        # Bouton: Créer une session

        if sortie["choix"] == [0, 0]:
            session = Session()
            if session.creer(window, resolution, temps_actuel, raccourcis):
                continuer_menu_session = True

        # Bouton: Choisir une session

        if sortie["choix"] == [0, 1]:
            session = Session()
            if session.choisir(window, resolution, temps_actuel, raccourcis):
                continuer_menu_session = True

        # Bouton: Editeur de niveaux

        elif sortie["choix"] == [0, 2]:
            etage_joueur = EtageEdit()
            etage_joueur.main(window, temps_actuel, raccourcis, resolution)

        # Bouton: Options

        elif sortie["choix"] == [0, 3]:
            options_utilisateur.modifier(window, temps_actuel, raccourcis, resolution)
            raccourcis = options_utilisateur.raccourcis

        # Bouton: Quitter le jeu

        elif sortie["choix"] == [0, 4]:
            continuer_menu_jeu = False

    elif sortie == 0:
        continue
    elif sortie == 1:
        exit(0)
    else:
        continue

    # Se préparer a aller dans le menu de session

    if continuer_menu_session:
        continuer_jeu = False

    # ------------------------------------------------------------------------------------------------------------------
    # BOUCLE DE LA SESSION
    # ------------------------------------------------------------------------------------------------------------------

    while continuer_menu_session:

        # Creer la page menu de session puis l'afficher

        boutons = ["Nouvelle partie", "Jouer à un niveau édité", "Quitter la session"]
        if session.utiliser_sauvegarde:
            boutons = ["Continuer le niveau sauvegardé"]+boutons

        page = Page([Menu(boutons, 0, 0, resolution["w"] if resolution["w"] >= 1024 else 1024,
                          resolution["h"] if resolution["h"] >= 576 else 576)], FOND)

        sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

        # Traiter la sortie

        if isinstance(sortie, dict):

            if session.utiliser_sauvegarde:
                decalage = 1
            else:
                decalage = 0

            # Bouton: Continuer le niveau sauvegardé

            if sortie["choix"] == [0, 0] and session.utiliser_sauvegarde:
                continuer_jeu = True

            # Bouton: Nouvelle partie

            elif sortie["choix"] == [0, decalage]:
                continuer_jeu = True
                session.utiliser_sauvegarde = False

            # Bouton: Jouer à un niveau edité

            elif sortie["choix"] == [0, 1+decalage]:
                niveau_actuel = choisir_niveau_jouer(window, temps_actuel, raccourcis, resolution)
                if niveau_actuel is not None:
                    continuer_jeu = True

            # Bouton: Quitter la session

            elif sortie["choix"] == [0, 2+decalage]:
                session.sauvegarder()
                continuer_menu_session = False

        elif sortie == 0:
            continue
        elif sortie == 1:
            save_and_quit(0, session)
        else:
            session.sauvegarder()
            continuer_menu_session = False

        # Se préparer a commencer le jeu

        if continuer_jeu:
            if not isinstance(niveau_actuel, str):
                niveau_actuel = 1

        # --------------------------------------------------------------------------------------------------------------
        # BOUCLE DU JEU
        # --------------------------------------------------------------------------------------------------------------

        while continuer_jeu:

            # Création / Chargement de l'étage

            continuer_niveau = True
            etage = Etage(niveau_actuel, not session.tutoriel_fait)

            if session.utiliser_sauvegarde and not isinstance(niveau_actuel, str):
                etage = session.recuperer_etage(window=window, resolution=resolution)
            else:
                etage.charger_etage(window=window, resolution=resolution)
                if not session.tutoriel_fait and niveau_actuel == 1:

                    # Afficher la cinématique d'intro si le joueur commence le premier niveau du tutoriel

                    pygame.init()

                    cinematique = pygame.movie.Movie("videos/intro.mpeg")
                    taille_ecran = sf.VideoMode.get_desktop_mode()
                    window = pygame.display.set_mode((taille_ecran.width, taille_ecran.height), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
                    surface_cinematique = pygame.Surface(cinematique.get_size())
                    cinematique.set_display(surface_cinematique)
                    cinematique.play()

                    while cinematique.get_busy():
                        window.blit(pygame.transform.scale(surface_cinematique, (taille_ecran.width, taille_ecran.height)), (0, 0))
                        pygame.display.update()
                        sf.sleep(sf.milliseconds(40))

                    pygame.quit()

                    # Reouvrir la fenêtre de jeu

                    window = sf.RenderWindow(sf.VideoMode(resolution["w"], resolution["h"], 32), "Endless-rooms",
                                             sf.Style.FULLSCREEN if options_utilisateur.fullscreen else sf.Style.DEFAULT)

            temps_niveau = sf.Clock()

            # ----------------------------------------------------------------------------------------------------------
            # BOUCLE DE L'ETAGE
            # ----------------------------------------------------------------------------------------------------------

            while continuer_niveau:

                # Affichage

                etage.afficher_image_jeu(window, resolution)
                etage.afficher_interface(window, resolution)
                etage.afficher_fenetre(window, resolution)
                gerer_fps(temps_actuel)
                window.display()

                # Gestion des evenements utilisateurs

                for event in window.events:

                    if isinstance(event, sf.ResizeEvent):
                        resolution["w"], resolution["h"] = event.size.x, event.size.y
                        window.view.reset((0, 0, resolution["w"], resolution["h"]))
                    if isinstance(event, sf.CloseEvent):
                        session.placer_etage(etage)
                        save_and_quit(0, session)

                    # MENU EN JEU

                    if isinstance(event, sf.KeyEvent):
                        if event.code == raccourcis["screenshot"][0] and event.released:
                            window.capture().to_file("screenshots/"+str(int(time()*1000))+".png")
                        if event.code == raccourcis["menu"][0] and event.released:

                            # Prendre une capture d'ecran comme fond de la page et enregistrer le temps du niveau

                            window.display()
                            fond_page = window.capture()
                            menu = True
                            fond_menu = sf.Sprite(sf.Texture.from_image(INTERFACE_IMAGE), (0, 108, 1024, 576))
                            etage.temps_niveau += temps_niveau.elapsed_time.seconds

                            # Boucle du menu

                            while menu:

                                # Creer la page du menu du jeu puis l'afficher

                                page = Page([Menu(("Continuer", "Recommencer le niveau", "Quitter la partie"),
                                                  (resolution["w"]-1024)//2, (resolution["h"]-576)//2,
                                                  1024, 576, fond=fond_menu)], fond_page)
                                sortie = page.afficher(window, temps_actuel, raccourcis, resolution)

                                # Traiter la sortie

                                if isinstance(sortie, dict):

                                    # Bouton: Continuer

                                    if sortie["choix"] == [0, 0]:
                                        etage.joueur.derniere_attaque.restart()

                                    # Bouton: Recommencer le niveau

                                    elif sortie["choix"] == [0, 1]:
                                        continuer_niveau = False

                                    # Bouton: Quitter la partie

                                    elif sortie["choix"] == [0, 2]:
                                        session.placer_etage(etage)
                                        continuer_niveau = False
                                        continuer_jeu = False

                                    menu = False

                                elif sortie == 0:
                                    continue
                                elif sortie == 1:
                                    session.placer_etage(etage)
                                    save_and_quit(0, session)
                                else:
                                    menu = False

                            temps_niveau.restart()

                # Gestion du jeu (toutes les fonctions qui font tourner le jeu)

                etage.tempo = (etage.tempo+1) % 24
                etage.tempo_lent = (etage.tempo_lent+1) % 24 if etage.tempo == 23 else etage.tempo_lent
                etage.deplacer_joueur(raccourcis)
                etage.creer_attaques_joueur(window, resolution)
                etage.deplacer_attaque()
                etage.detruire_attaque()
                etage.gerer_portes()
                etage.deplacer_monstres()
                etage.gerer_mort_monstres()
                etage.activer_monstres(resolution)
                etage.detecter_fenetre()
                etage.creer_attaques_pieges(resolution)

                # Gestion des possibilités d'arrêt de la boucle

                if etage.joueur.vie == 0:
                    continuer_niveau = False

                if etage.blocs[etage.joueur.x_hitbox//64, etage.joueur.y_hitbox//64] == 3:
                    if isinstance(etage.level, int):
                        continuer_niveau = False
                        if etage.mode_tutoriel and niveau_actuel == 1:
                            niveau_actuel = 1
                            session.tutoriel_fait = True
                        else:
                            etage.temps_niveau += temps_niveau.elapsed_time.seconds
                            if not etage.afficher_temps_niveau(window, temps_actuel, raccourcis, resolution, session):
                                continuer_jeu = False
                            del etage.temps_niveau

                            niveau_actuel += 1
                    else:
                        continuer_niveau = False
                        continuer_jeu = False

        # Réinitialiser "niveau_actuel" si jamais le niveau joué était un niveau édité ou en ligne

        niveau_actuel = int()
