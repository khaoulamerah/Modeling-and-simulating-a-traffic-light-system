"""
SIMULATION_VISUELLE.PY - Interface graphique moderne et professionnelle
Projet : Simulation de Feux de Circulation
Responsable : Tasnim

UI Moderne :
- Voitures ultra-réalistes avec dégradés et ombres
- Files d'attente qui s'allongent dynamiquement
- Feux de circulation avec ombres et effets lumineux
- Passages piétons et panneaux de signalisation
- Design centré avec bordures arrondies et couleurs propres
"""

import pygame
import sys
import threading
import time
from queue import Queue
from dataclasses import dataclass
from typing import List
import math

# Import des modules de simulation
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'sarah_implementation', 'src'))

import simpy
from feux import SystemeFeux, ConfigurationFeux, CouleurFeu, EtatSysteme
from vehicule import GenerateurVehicules, Vehicule, Direction
from intersection import Intersection
from statistiques import CollecteurDonnees


# ========== CONFIGURATION GRAPHIQUE ==========

# Palette moderne
FOND_APP = (240, 242, 245)
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
ASPHALTE = (45, 52, 58)
LIGNE_JAUNE = (255, 215, 0)
LIGNE_BLANCHE = (250, 250, 250)
PASSAGE_PIETON = (245, 245, 245)

# Feux
VERT_FEU = (46, 213, 115)
JAUNE_FEU = (255, 184, 0)
ROUGE_FEU = (255, 71, 87)
FEU_ETEINT = (40, 40, 40)

# Voitures
BLEU_VOITURE = (52, 152, 219)
BLEU_FONCE = (41, 128, 185)
ORANGE_VOITURE = (255, 127, 80)
ORANGE_FONCE = (255, 99, 71)

# UI
COULEUR_PANEL = (255, 255, 255)
COULEUR_TEXTE = (44, 62, 80)
COULEUR_ACCENT = (52, 152, 219)
OMBRE = (0, 0, 0, 40)

# Dimensions
LARGEUR_FENETRE = 1300
HAUTEUR_FENETRE = 600
LARGEUR_ROUTE = 150
TAILLE_VOITURE_L = 55
TAILLE_VOITURE_W = 32


# ========== FONCTIONS DE DESSIN ==========

def creer_surface_ombre(largeur, hauteur, rayon=10, offset=6):
    """Crée une surface d'ombre portée"""
    surface = pygame.Surface((largeur + offset*2, hauteur + offset*2), pygame.SRCALPHA)
    for i in range(offset):
        alpha = 30 - i * 4
        pygame.draw.rect(surface, (0, 0, 0, alpha), 
                        (i, i, largeur + (offset-i)*2, hauteur + (offset-i)*2),
                        border_radius=rayon)
    return surface


def dessiner_voiture_realiste_horizontale(surface, x, y, largeur, hauteur, couleur_base, couleur_fonce):
    """Dessine une voiture ultra-réaliste orientée horizontalement"""
    # Ombre de la voiture
    ombre = pygame.Surface((largeur + 8, hauteur + 8), pygame.SRCALPHA)
    pygame.draw.rect(ombre, (0, 0, 0, 50), (4, 4, largeur, hauteur), border_radius=8)
    surface.blit(ombre, (x - 4, y - 4))
    
    # Corps principal avec dégradé
    pygame.draw.rect(surface, couleur_base, (x, y, largeur, hauteur), border_radius=8)
    
    # Toit (partie supérieure plus foncée)
    pygame.draw.rect(surface, couleur_fonce, (x + largeur*0.3, y + 4, largeur*0.4, hauteur-8), border_radius=5)
    
    # Vitres avant
    vitre_color = (100, 150, 180, 200)
    vitre_surf = pygame.Surface((int(largeur*0.18), int(hauteur-10)), pygame.SRCALPHA)
    pygame.draw.rect(vitre_surf, vitre_color, (0, 0, int(largeur*0.18), int(hauteur-10)), border_radius=3)
    surface.blit(vitre_surf, (x + largeur*0.65, y + 5))
    
    # Vitres arrière
    surface.blit(vitre_surf, (x + largeur*0.32, y + 5))
    
    # Phares avant (jaunes)
    pygame.draw.circle(surface, (255, 255, 150), (int(x + largeur - 4), int(y + hauteur*0.25)), 4)
    pygame.draw.circle(surface, (255, 255, 150), (int(x + largeur - 4), int(y + hauteur*0.75)), 4)
    
    # Feux arrière (rouges)
    pygame.draw.circle(surface, (200, 50, 50), (int(x + 4), int(y + hauteur*0.25)), 3)
    pygame.draw.circle(surface, (200, 50, 50), (int(x + 4), int(y + hauteur*0.75)), 3)
    
    # Roues
    roue_color = (30, 30, 30)
    rayon_roue = 6
    # Roues avant
    pygame.draw.circle(surface, roue_color, (int(x + largeur*0.8), int(y - 2)), rayon_roue)
    pygame.draw.circle(surface, roue_color, (int(x + largeur*0.8), int(y + hauteur + 2)), rayon_roue)
    # Roues arrière
    pygame.draw.circle(surface, roue_color, (int(x + largeur*0.25), int(y - 2)), rayon_roue)
    pygame.draw.circle(surface, roue_color, (int(x + largeur*0.25), int(y + hauteur + 2)), rayon_roue)
    
    # Jantes (centres gris)
    pygame.draw.circle(surface, (80, 80, 80), (int(x + largeur*0.8), int(y - 2)), 3)
    pygame.draw.circle(surface, (80, 80, 80), (int(x + largeur*0.8), int(y + hauteur + 2)), 3)
    pygame.draw.circle(surface, (80, 80, 80), (int(x + largeur*0.25), int(y - 2)), 3)
    pygame.draw.circle(surface, (80, 80, 80), (int(x + largeur*0.25), int(y + hauteur + 2)), 3)
    
    # Contour
    pygame.draw.rect(surface, NOIR, (x, y, largeur, hauteur), 2, border_radius=8)


def dessiner_voiture_realiste_verticale(surface, x, y, largeur, hauteur, couleur_base, couleur_fonce):
    """Dessine une voiture ultra-réaliste orientée verticalement"""
    # Ombre
    ombre = pygame.Surface((largeur + 8, hauteur + 8), pygame.SRCALPHA)
    pygame.draw.rect(ombre, (0, 0, 0, 50), (4, 4, largeur, hauteur), border_radius=8)
    surface.blit(ombre, (x - 4, y - 4))
    
    # Corps
    pygame.draw.rect(surface, couleur_base, (x, y, largeur, hauteur), border_radius=8)
    
    # Toit
    pygame.draw.rect(surface, couleur_fonce, (x + 4, y + hauteur*0.3, largeur-8, hauteur*0.4), border_radius=5)
    
    # Vitres
    vitre_color = (100, 150, 180, 200)
    vitre_surf = pygame.Surface((int(largeur-10), int(hauteur*0.18)), pygame.SRCALPHA)
    pygame.draw.rect(vitre_surf, vitre_color, (0, 0, int(largeur-10), int(hauteur*0.18)), border_radius=3)
    surface.blit(vitre_surf, (x + 5, y + hauteur*0.65))
    surface.blit(vitre_surf, (x + 5, y + hauteur*0.32))
    
    # Phares avant
    pygame.draw.circle(surface, (255, 255, 150), (int(x + largeur*0.25), int(y + hauteur - 4)), 4)
    pygame.draw.circle(surface, (255, 255, 150), (int(x + largeur*0.75), int(y + hauteur - 4)), 4)
    
    # Feux arrière
    pygame.draw.circle(surface, (200, 50, 50), (int(x + largeur*0.25), int(y + 4)), 3)
    pygame.draw.circle(surface, (200, 50, 50), (int(x + largeur*0.75), int(y + 4)), 3)
    
    # Roues
    roue_color = (30, 30, 30)
    rayon_roue = 6
    pygame.draw.circle(surface, roue_color, (int(x - 2), int(y + hauteur*0.8)), rayon_roue)
    pygame.draw.circle(surface, roue_color, (int(x + largeur + 2), int(y + hauteur*0.8)), rayon_roue)
    pygame.draw.circle(surface, roue_color, (int(x - 2), int(y + hauteur*0.25)), rayon_roue)
    pygame.draw.circle(surface, roue_color, (int(x + largeur + 2), int(y + hauteur*0.25)), rayon_roue)
    
    # Jantes
    pygame.draw.circle(surface, (80, 80, 80), (int(x - 2), int(y + hauteur*0.8)), 3)
    pygame.draw.circle(surface, (80, 80, 80), (int(x + largeur + 2), int(y + hauteur*0.8)), 3)
    pygame.draw.circle(surface, (80, 80, 80), (int(x - 2), int(y + hauteur*0.25)), 3)
    pygame.draw.circle(surface, (80, 80, 80), (int(x + largeur + 2), int(y + hauteur*0.25)), 3)
    
    # Contour
    pygame.draw.rect(surface, NOIR, (x, y, largeur, hauteur), 2, border_radius=8)


def dessiner_feu_tricolore_moderne(surface, x, y, couleur_active):
    """Dessine un feu tricolore moderne avec ombre et effet lumineux"""
    # Ombre du poteau
    pygame.draw.rect(surface, (0, 0, 0, 30), (x - 3, y + 95, 10, 50))
    
    # Poteau
    pygame.draw.rect(surface, (60, 60, 60), (x - 5, y + 90, 10, 50))
    
    # Ombre du boîtier
    ombre_feu = pygame.Surface((55, 105), pygame.SRCALPHA)
    pygame.draw.rect(ombre_feu, (0, 0, 0, 60), (3, 3, 50, 100), border_radius=12)
    surface.blit(ombre_feu, (x - 28, y - 2))
    
    # Boîtier
    pygame.draw.rect(surface, (35, 35, 35), (x - 25, y, 50, 95), border_radius=12)
    pygame.draw.rect(surface, (20, 20, 20), (x - 25, y, 50, 95), 3, border_radius=12)
    
    # Lumières
    feux = [
        (y + 18, ROUGE_FEU, couleur_active == ROUGE_FEU),
        (y + 47, JAUNE_FEU, couleur_active == JAUNE_FEU),
        (y + 76, VERT_FEU, couleur_active == VERT_FEU)
    ]
    
    for y_pos, couleur, actif in feux:
        # Fond du cercle (noir)
        pygame.draw.circle(surface, FEU_ETEINT, (x, int(y_pos)), 14)
        
        # Lumière
        if actif:
            # Halo lumineux
            for i in range(4):
                alpha = 40 - i * 8
                rayon = 18 + i * 4
                halo = pygame.Surface((rayon*2, rayon*2), pygame.SRCALPHA)
                pygame.draw.circle(halo, (*couleur[:3], alpha), (rayon, rayon), rayon)
                surface.blit(halo, (x - rayon, int(y_pos) - rayon))
            
            # Lumière principale
            pygame.draw.circle(surface, couleur, (x, int(y_pos)), 13)
            
            # Reflet (effet brillant)
            pygame.draw.circle(surface, (255, 255, 255, 100), (int(x - 4), int(y_pos - 4)), 4)
        else:
            # Lumière éteinte
            couleur_eteinte = (couleur[0]//4, couleur[1]//4, couleur[2]//4)
            pygame.draw.circle(surface, couleur_eteinte, (x, int(y_pos)), 13)
        
        # Contour
        pygame.draw.circle(surface, NOIR, (x, int(y_pos)), 13, 2)


def dessiner_passage_pieton(surface, x, y, largeur, hauteur, horizontal=True):
    """Dessine un passage piéton"""
    nb_bandes = 8
    if horizontal:
        largeur_bande = largeur // nb_bandes
        for i in range(0, nb_bandes, 2):
            pygame.draw.rect(surface, PASSAGE_PIETON, 
                           (x + i * largeur_bande, y, largeur_bande - 2, hauteur))
    else:
        hauteur_bande = hauteur // nb_bandes
        for i in range(0, nb_bandes, 2):
            pygame.draw.rect(surface, PASSAGE_PIETON,
                           (x, y + i * hauteur_bande, largeur, hauteur_bande - 2))


def dessiner_panneau_stop(surface, x, y):
    """Dessine un panneau STOP"""
    # Poteau
    pygame.draw.rect(surface, (80, 80, 80), (x - 3, y + 30, 6, 25))
    
    # Ombre panneau
    ombre = pygame.Surface((50, 50), pygame.SRCALPHA)
    points = [(25, 2), (46, 13), (46, 37), (25, 48), (4, 37), (4, 13)]
    pygame.draw.polygon(ombre, (0, 0, 0, 50), points)
    surface.blit(ombre, (x - 22, y - 2))
    
    # Panneau octogonal (rouge)
    points = [(x, y), (x + 20, y), (x + 28, y + 8), (x + 28, y + 20),
              (x + 20, y + 28), (x, y + 28), (x - 8, y + 20), (x - 8, y + 8)]
    pygame.draw.polygon(surface, (220, 50, 50), points)
    pygame.draw.polygon(surface, BLANC, points, 3)
    
    # Texte STOP
    font = pygame.font.Font(None, 16)
    texte = font.render("STOP", True, BLANC)
    surface.blit(texte, (x + 2, y + 10))


@dataclass
class VoitureGraphique:
    vehicule: Vehicule
    x: float
    y: float
    couleur_base: tuple
    couleur_fonce: tuple
    direction: str
    en_attente: bool = True


class CarrefourGraphique:
    """Gère l'affichage moderne du carrefour"""
    
    def __init__(self, largeur: int, hauteur: int):
        self.largeur = largeur
        self.hauteur = hauteur
        
        # Centre parfaitement l'intersection
        self.centre_x = largeur // 2
        self.centre_y = hauteur // 2
        
        self.voitures_voie_a: List[VoitureGraphique] = []
        self.voitures_voie_b: List[VoitureGraphique] = []
        
        self.couleur_feu_a = ROUGE_FEU
        self.couleur_feu_b = ROUGE_FEU
        
        # Positions des feux (ajustées pour centrage)
        self.pos_feu_a = (self.centre_x - 180, self.centre_y - 20)
        self.pos_feu_b = (self.centre_x - 20, self.centre_y - 180)
        
        self.stats = {
            'voie_a_attente': 0,
            'voie_b_attente': 0,
            'voie_a_servis': 0,
            'voie_b_servis': 0,
            'temps_attente_a': 0,
            'temps_attente_b': 0
        }
    
    def dessiner_routes(self, surface):
        """Dessine les routes avec passages piétons et marquages"""
        # Route horizontale
        pygame.draw.rect(surface, ASPHALTE,
                        (0, self.centre_y - LARGEUR_ROUTE//2,
                         self.largeur, LARGEUR_ROUTE))
        
        # Bordures jaunes
        pygame.draw.rect(surface, LIGNE_JAUNE,
                        (0, self.centre_y - LARGEUR_ROUTE//2 - 3,
                         self.largeur, 4))
        pygame.draw.rect(surface, LIGNE_JAUNE,
                        (0, self.centre_y + LARGEUR_ROUTE//2,
                         self.largeur, 4))
        
        # Ligne centrale discontinue
        for i in range(0, self.largeur, 60):
            if not (self.centre_x - LARGEUR_ROUTE//2 < i < self.centre_x + LARGEUR_ROUTE//2):
                pygame.draw.rect(surface, LIGNE_BLANCHE,
                               (i, self.centre_y - 3, 35, 6))
        
        # Route verticale
        pygame.draw.rect(surface, ASPHALTE,
                        (self.centre_x - LARGEUR_ROUTE//2, 0,
                         LARGEUR_ROUTE, self.hauteur))
        
        # Bordures
        pygame.draw.rect(surface, LIGNE_JAUNE,
                        (self.centre_x - LARGEUR_ROUTE//2 - 3, 0,
                         4, self.hauteur))
        pygame.draw.rect(surface, LIGNE_JAUNE,
                        (self.centre_x + LARGEUR_ROUTE//2, 0,
                         4, self.hauteur))
        
        # Ligne centrale
        for i in range(0, self.hauteur, 60):
            if not (self.centre_y - LARGEUR_ROUTE//2 < i < self.centre_y + LARGEUR_ROUTE//2):
                pygame.draw.rect(surface, LIGNE_BLANCHE,
                               (self.centre_x - 3, i, 6, 35))
        
        # Passages piétons
        # Horizontal gauche
        dessiner_passage_pieton(surface,
                               self.centre_x - LARGEUR_ROUTE//2 - 80,
                               self.centre_y - LARGEUR_ROUTE//2 + 10,
                               70, LARGEUR_ROUTE - 20, True)
        # Horizontal droite
        dessiner_passage_pieton(surface,
                               self.centre_x + LARGEUR_ROUTE//2 + 10,
                               self.centre_y - LARGEUR_ROUTE//2 + 10,
                               70, LARGEUR_ROUTE - 20, True)
        # Vertical haut
        dessiner_passage_pieton(surface,
                               self.centre_x - LARGEUR_ROUTE//2 + 10,
                               self.centre_y - LARGEUR_ROUTE//2 - 80,
                               LARGEUR_ROUTE - 20, 70, False)
        # Vertical bas
        dessiner_passage_pieton(surface,
                               self.centre_x - LARGEUR_ROUTE//2 + 10,
                               self.centre_y + LARGEUR_ROUTE//2 + 10,
                               LARGEUR_ROUTE - 20, 70, False)
        
        # Panneaux STOP
        dessiner_panneau_stop(surface, self.centre_x - 200, self.centre_y - 60)
        dessiner_panneau_stop(surface, self.centre_x - 60, self.centre_y - 200)
        
        # Zone d'intersection
        pygame.draw.rect(surface, (55, 62, 68),
                        (self.centre_x - LARGEUR_ROUTE//2,
                         self.centre_y - LARGEUR_ROUTE//2,
                         LARGEUR_ROUTE, LARGEUR_ROUTE))
    
    def dessiner_feux(self, surface):
        """Dessine les feux de circulation"""
        dessiner_feu_tricolore_moderne(surface, self.pos_feu_a[0], self.pos_feu_a[1], 
                                      self.couleur_feu_a)
        
        font = pygame.font.Font(None, 24)
        label = font.render("Voie A", True, COULEUR_TEXTE)
        surface.blit(label, (self.pos_feu_a[0] - 25, self.pos_feu_a[1] - 25))
        
        dessiner_feu_tricolore_moderne(surface, self.pos_feu_b[0], self.pos_feu_b[1],
                                      self.couleur_feu_b)
        
        label = font.render("Voie B", True, COULEUR_TEXTE)
        surface.blit(label, (self.pos_feu_b[0] - 25, self.pos_feu_b[1] - 25))
    
    def dessiner_voitures(self, surface):
        """Dessine toutes les voitures"""
        for voiture in self.voitures_voie_a:
            dessiner_voiture_realiste_horizontale(surface, voiture.x, voiture.y,
                                                 TAILLE_VOITURE_L, TAILLE_VOITURE_W,
                                                 voiture.couleur_base, voiture.couleur_fonce)
        
        for voiture in self.voitures_voie_b:
            dessiner_voiture_realiste_verticale(surface, voiture.x, voiture.y,
                                               TAILLE_VOITURE_W, TAILLE_VOITURE_L,
                                               voiture.couleur_base, voiture.couleur_fonce)
    
    def dessiner_stats(self, surface):
        """Affiche les statistiques dans un panel moderne"""
        panneau_x = self.largeur - 300
        panneau_y = 30
        panneau_w = 280
        panneau_h = 380
        
        # Ombre du panneau
        ombre = creer_surface_ombre(panneau_w, panneau_h, 15, 8)
        surface.blit(ombre, (panneau_x - 8, panneau_y - 8))
        
        # Fond du panneau
        pygame.draw.rect(surface, COULEUR_PANEL,
                        (panneau_x, panneau_y, panneau_w, panneau_h),
                        border_radius=15)
        pygame.draw.rect(surface, (200, 200, 200),
                        (panneau_x, panneau_y, panneau_w, panneau_h),
                        2, border_radius=15)
        
        # Titre
        font_titre = pygame.font.Font(None, 32)
        titre = font_titre.render("📊 STATISTIQUES", True, COULEUR_TEXTE)
        surface.blit(titre, (panneau_x + 50, panneau_y + 15))
        
        # Ligne de séparation
        pygame.draw.line(surface, (220, 220, 220),
                        (panneau_x + 20, panneau_y + 60),
                        (panneau_x + panneau_w - 20, panneau_y + 60), 2)
        
        font_section = pygame.font.Font(None, 26)
        font_stats = pygame.font.Font(None, 22)
        
        y_offset = panneau_y + 80
        
        # Voie A
        section = font_section.render("🚗 VOIE A", True, BLEU_VOITURE)
        surface.blit(section, (panneau_x + 25, y_offset))
        y_offset += 40
        
        stats_a = [
            f"En attente: {self.stats['voie_a_attente']}",
            f"Servis: {self.stats['voie_a_servis']}",
            f"Attente moyenne: {self.stats['temps_attente_a']:.1f}s"
        ]
        
        for stat in stats_a:
            texte = font_stats.render(stat, True, COULEUR_TEXTE)
            surface.blit(texte, (panneau_x + 40, y_offset))
            y_offset += 30
        
        y_offset += 15
        pygame.draw.line(surface, (220, 220, 220),
                        (panneau_x + 20, y_offset),
                        (panneau_x + panneau_w - 20, y_offset), 2)
        y_offset += 25
        
        # Voie B
        section = font_section.render("🚙 VOIE B", True, ORANGE_VOITURE)
        surface.blit(section, (panneau_x + 25, y_offset))
        y_offset += 40
        
        stats_b = [
            f"En attente: {self.stats['voie_b_attente']}",
            f"Servis: {self.stats['voie_b_servis']}",
            f"Attente moyenne: {self.stats['temps_attente_b']:.1f}s"
        ]
        
        for stat in stats_b:
            texte = font_stats.render(stat, True, COULEUR_TEXTE)
            surface.blit(texte, (panneau_x + 40, y_offset))
            y_offset += 30

    def ajouter_voiture_a(self, vehicule: Vehicule):
        """Ajoute une voiture dans la file d'attente A (croît vers la gauche)"""
        nb_voitures = len([v for v in self.voitures_voie_a if v.en_attente])
        x = self.centre_x - 250 - (nb_voitures * 65)
        y = self.centre_y - TAILLE_VOITURE_W // 2
        
        voiture = VoitureGraphique(
            vehicule=vehicule,
            x=x,
            y=y,
            couleur_base=BLEU_VOITURE,
            couleur_fonce=BLEU_FONCE,
            direction='horizontale',
            en_attente=True
        )
        self.voitures_voie_a.append(voiture)
    
    def ajouter_voiture_b(self, vehicule: Vehicule):
        """Ajoute une voiture dans la file d'attente B (croît vers le haut)"""
        nb_voitures = len([v for v in self.voitures_voie_b if v.en_attente])
        x = self.centre_x - TAILLE_VOITURE_W // 2
        y = self.centre_y - 250 - (nb_voitures * 65)
        
        voiture = VoitureGraphique(
            vehicule=vehicule,
            x=x,
            y=y,
            couleur_base=ORANGE_VOITURE,
            couleur_fonce=ORANGE_FONCE,
            direction='verticale',
            en_attente=True
        )
        self.voitures_voie_b.append(voiture)
    
    def faire_passer_voiture_a(self):
        """Fait passer une voiture de la voie A"""
        for voiture in self.voitures_voie_a:
            if voiture.en_attente:
                voiture.en_attente = False
                return voiture
        return None
    
    def faire_passer_voiture_b(self):
        """Fait passer une voiture de la voie B"""
        for voiture in self.voitures_voie_b:
            if voiture.en_attente:
                voiture.en_attente = False
                return voiture
        return None
    
    def animer_voitures(self):
        """Anime les voitures qui passent"""
        for voiture in self.voitures_voie_a[:]:
            if not voiture.en_attente:
                voiture.x += 5
                if voiture.x > self.largeur + 50:
                    self.voitures_voie_a.remove(voiture)
        
        for voiture in self.voitures_voie_b[:]:
            if not voiture.en_attente:
                voiture.y += 5
                if voiture.y > self.hauteur + 50:
                    self.voitures_voie_b.remove(voiture)


class BoutonModerne:
    """Bouton avec design moderne"""
    def __init__(self, x, y, largeur, hauteur, texte, couleur):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.texte = texte
        self.couleur = couleur
        self.couleur_hover = tuple(min(c + 30, 255) for c in couleur)
        self.hover = False
    
    def dessiner(self, surface):
        # Ombre
        ombre = creer_surface_ombre(self.rect.width, self.rect.height, 12, 6)
        surface.blit(ombre, (self.rect.x - 6, self.rect.y - 6))
        
        # Bouton
        couleur = self.couleur_hover if self.hover else self.couleur
        pygame.draw.rect(surface, couleur, self.rect, border_radius=12)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2, border_radius=12)
        
        # Texte
        font = pygame.font.Font(None, 32)
        texte = font.render(self.texte, True, BLANC)
        texte_rect = texte.get_rect(center=self.rect.center)
        surface.blit(texte, texte_rect)
    
    def verifier_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)
    
    def est_clique(self, pos):
        return self.rect.collidepoint(pos)


# ========== GESTIONNAIRE DE SIMULATION ==========

class GestionnaireSimulation:
    """Fait le lien entre SimPy et Pygame"""
    
    def __init__(self, carrefour_graphique: CarrefourGraphique):
        self.carrefour = carrefour_graphique
        self.env = None
        self.evenements = Queue()
        self.thread_simulation = None
        self.simulation_active = False
        self.nom_scenario = "Scénario par défaut"  # Nom du scénario courant

    def demarrer_simulation(self, lambda_a=0.3, lambda_b=0.3, config_feux=None, nom_scenario="Scénario par défaut"):
        self.nom_scenario = nom_scenario  # Sauvegarde le nom du scénario
        
        if config_feux is None:
            config_feux = ConfigurationFeux()
        
        self.simulation_active = True
        self.thread_simulation = threading.Thread(
            target=self._executer_simulation,
            args=(lambda_a, lambda_b, config_feux),
            daemon=True
        )
        self.thread_simulation.start()
    
    def _executer_simulation(self, lambda_a, lambda_b, config_feux):
        self.env = simpy.Environment()
        systeme_feux = SystemeFeux(self.env, config_feux)
        intersection = Intersection(self.env, systeme_feux)
        generateur = GenerateurVehicules(self.env, lambda_a, lambda_b)
        
        self.env.process(self._gerer_feux(config_feux))
        self.env.process(self._generer_voie_a(generateur))
        self.env.process(self._generer_voie_b(generateur))
        
        while self.simulation_active:
            self.env.run(until=self.env.now + 0.1)
            time.sleep(0.05)
    
    def _gerer_feux(self, config):
        while True:
            self.evenements.put(('feu_a', VERT_FEU))
            self.evenements.put(('feu_b', ROUGE_FEU))
            yield self.env.timeout(config.duree_vert_a)
            
            self.evenements.put(('feu_a', JAUNE_FEU))
            yield self.env.timeout(config.duree_jaune)
            
            self.evenements.put(('feu_a', ROUGE_FEU))
            self.evenements.put(('feu_b', VERT_FEU))
            yield self.env.timeout(config.duree_vert_b)
            
            self.evenements.put(('feu_b', JAUNE_FEU))
            yield self.env.timeout(config.duree_jaune)
            
            self.evenements.put(('feu_b', ROUGE_FEU))
            yield self.env.timeout(config.duree_pietons)
    
    def _generer_voie_a(self, generateur):
        compteur = 0
        while True:
            yield self.env.timeout(generateur.temps_inter_arrivee(generateur.lambda_a))
            compteur += 1
            vehicule = Vehicule(compteur, Direction.VOIE_A, self.env.now)
            self.evenements.put(('nouvelle_voiture_a', vehicule))
            
            while self.carrefour.couleur_feu_a != VERT_FEU:
                yield self.env.timeout(0.1)
            
            self.evenements.put(('passer_voiture_a', vehicule))
            vehicule.temps_depart = self.env.now
            vehicule.temps_attente = vehicule.temps_depart - vehicule.temps_arrivee
            self.evenements.put(('stats_a', vehicule.temps_attente))
    
    def _generer_voie_b(self, generateur):
        compteur = 0
        while True:
            yield self.env.timeout(generateur.temps_inter_arrivee(generateur.lambda_b))
            compteur += 1
            vehicule = Vehicule(compteur, Direction.VOIE_B, self.env.now)
            self.evenements.put(('nouvelle_voiture_b', vehicule))
            
            while self.carrefour.couleur_feu_b != VERT_FEU:
                yield self.env.timeout(0.1)
            
            self.evenements.put(('passer_voiture_b', vehicule))
            vehicule.temps_depart = self.env.now
            vehicule.temps_attente = vehicule.temps_depart - vehicule.temps_arrivee
            self.evenements.put(('stats_b', vehicule.temps_attente))
    
    def traiter_evenements(self):
        while not self.evenements.empty():
            evenement = self.evenements.get()
            type_evt = evenement[0]
            
            if type_evt == 'feu_a':
                self.carrefour.couleur_feu_a = evenement[1]
            elif type_evt == 'feu_b':
                self.carrefour.couleur_feu_b = evenement[1]
            elif type_evt == 'nouvelle_voiture_a':
                self.carrefour.ajouter_voiture_a(evenement[1])
                self.carrefour.stats['voie_a_attente'] += 1
            elif type_evt == 'nouvelle_voiture_b':
                self.carrefour.ajouter_voiture_b(evenement[1])
                self.carrefour.stats['voie_b_attente'] += 1
            elif type_evt == 'passer_voiture_a':
                self.carrefour.faire_passer_voiture_a()
                self.carrefour.stats['voie_a_attente'] = max(0, self.carrefour.stats['voie_a_attente'] - 1)
                self.carrefour.stats['voie_a_servis'] += 1
            elif type_evt == 'passer_voiture_b':
                self.carrefour.faire_passer_voiture_b()
                self.carrefour.stats['voie_b_attente'] = max(0, self.carrefour.stats['voie_b_attente'] - 1)
                self.carrefour.stats['voie_b_servis'] += 1
            elif type_evt == 'stats_a':
                temps = evenement[1]
                n = self.carrefour.stats['voie_a_servis']
                if n > 0:
                    moy = self.carrefour.stats['temps_attente_a']
                    self.carrefour.stats['temps_attente_a'] = (moy * (n-1) + temps) / n
            elif type_evt == 'stats_b':
                temps = evenement[1]
                n = self.carrefour.stats['voie_b_servis']
                if n > 0:
                    moy = self.carrefour.stats['temps_attente_b']
                    self.carrefour.stats['temps_attente_b'] = (moy * (n-1) + temps) / n
    
    def arreter_simulation(self):
        self.simulation_active = False
        if self.thread_simulation:
            self.thread_simulation.join(timeout=1)


# ========== BOUCLE PRINCIPALE ==========

def main():
    pygame.init()
    screen = pygame.display.set_mode((LARGEUR_FENETRE, HAUTEUR_FENETRE))
    pygame.display.set_caption("🚦 Simulation Feux de Circulation - Interface Moderne")
    clock = pygame.time.Clock()
    
    carrefour = CarrefourGraphique(LARGEUR_FENETRE, HAUTEUR_FENETRE)
    gestionnaire = GestionnaireSimulation(carrefour)

    # Liste des scénarios
    scenarios = [
        {"nom": "Scénario 1 : Trafic Léger", "lambda_a": 0.3, "lambda_b": 0.3, "T_A": 30, "T_B": 25},
        {"nom": "Scénario 2 : Asymétrique", "lambda_a": 0.4, "lambda_b": 0.4, "T_A": 40, "T_B": 20},
        {"nom": "Scénario 3 : Optimisé", "lambda_a": 0.3, "lambda_b": 0.3, "T_A": 28, "T_B": 28}
    ]

    # Choisis ici le scénario que tu veux lancer (0, 1 ou 2)
    scenario_choisi = 2  # Change ce numéro : 0 = Scénario 1, 1 = Scénario 2, 2 = Scénario 3

    sc = scenarios[scenario_choisi]
    config = ConfigurationFeux(duree_vert_a=sc["T_A"], duree_vert_b=sc["T_B"])

    gestionnaire.demarrer_simulation(
        lambda_a=sc["lambda_a"],
        lambda_b=sc["lambda_b"],
        config_feux=config,
        nom_scenario=sc["nom"]  # Le nom est transmis ici
    )
    
    # Bouton de sortie
    bouton_quitter = BoutonModerne(LARGEUR_FENETRE - 190, HAUTEUR_FENETRE - 80, 
                                   170, 55, "✕ QUITTER", (231, 76, 60))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                bouton_quitter.verifier_hover(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if bouton_quitter.est_clique(event.pos):
                    running = False
        
        gestionnaire.traiter_evenements()
        carrefour.animer_voitures()
        
        # Fond
        screen.fill(FOND_APP)
        
        # Dessiner tout
        carrefour.dessiner_routes(screen)
        carrefour.dessiner_feux(screen)
        carrefour.dessiner_voitures(screen)
        carrefour.dessiner_stats(screen)
        bouton_quitter.dessiner(screen)
        
        # Temps de simulation
        if gestionnaire.env:
            temps_x = 30
            temps_y = 30
            temps_w = 220
            temps_h = 70
            
            ombre = creer_surface_ombre(temps_w, temps_h, 12, 6)
            screen.blit(ombre, (temps_x - 6, temps_y - 6))
            
            pygame.draw.rect(screen, COULEUR_PANEL,
                           (temps_x, temps_y, temps_w, temps_h),
                           border_radius=12)
            pygame.draw.rect(screen, (200, 200, 200),
                           (temps_x, temps_y, temps_w, temps_h),
                           2, border_radius=12)
            
            font = pygame.font.Font(None, 32)
            texte = font.render("⏱️ Temps de simulation", True, COULEUR_TEXTE)
            screen.blit(texte, (temps_x + 15, temps_y + 12))
            
            font_temps = pygame.font.Font(None, 36)
            temps_txt = font_temps.render(f"{gestionnaire.env.now:.1f}s", True, COULEUR_ACCENT)
            screen.blit(temps_txt, (temps_x + 70, temps_y + 38))
        
        # Affichage du nom du scénario (dynamique)
        scenario_nom = gestionnaire.nom_scenario
        
        font_scenario = pygame.font.Font(None, 50)
        text_surf = font_scenario.render(scenario_nom, True, COULEUR_ACCENT)
        text_rect = text_surf.get_rect(center=(LARGEUR_FENETRE // 2, 80))
        
        bg_rect = text_rect.inflate(60, 30)
        pygame.draw.rect(screen, COULEUR_PANEL, bg_rect, border_radius=20)
        pygame.draw.rect(screen, (180, 180, 180), bg_rect, 3, border_radius=20)
        
        ombre_bg = creer_surface_ombre(bg_rect.width, bg_rect.height, 20, 8)
        screen.blit(ombre_bg, (bg_rect.x - 8, bg_rect.y - 8))
        
        screen.blit(text_surf, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    gestionnaire.arreter_simulation()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()