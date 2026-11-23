"""Prédimensionnement indicatif des poteaux et semelles."""
from __future__ import annotations
import math
from .elements import Projet
from .charges import descente_de_charges


def arrondir_superieur(valeur: float, pas: float = 0.05) -> float:
    """Arrondit une dimension au multiple supérieur du pas choisi."""
    return math.ceil((valeur - 1e-12) / pas) * pas


def predimensionner_poteaux(projet: Projet) -> list[dict[str, float | str]]:
    """Propose une section carrée à partir d'une contrainte simplifiée."""
    resultats = []
    for charge in descente_de_charges(projet):
        effort = float(charge["effort_kn"])
        aire = effort / projet.contrainte_admissible_beton_kn_m2
        cote_theorique = math.sqrt(aire)
        cote_adopte = max(0.20, arrondir_superieur(cote_theorique))
        resultats.append({
            "type": str(charge["type"]),
            "effort_kn": effort,
            "aire_minimale_m2": aire,
            "cote_theorique_m": cote_theorique,
            "cote_adopte_m": cote_adopte,
        })
    return resultats


def predimensionner_semelles(projet: Projet) -> list[dict[str, float | str]]:
    """Propose des semelles carrées selon la règle pédagogique du sujet.

    La formule du support est B >= racine(N / 187,5) pour q_sol=200 kPa,
    ce qui revient à réserver 12,5 kPa. Pour une autre contrainte de sol,
    la marge de 12,5 kPa est conservée : B = racine(N/(q_sol-12,5)).
    """
    resultats = []
    q_effectif = projet.contrainte_admissible_sol_kpa - 12.5
    if q_effectif <= 0:
        raise ValueError("La contrainte admissible du sol doit être supérieure à 12,5 kPa.")
    for charge in descente_de_charges(projet):
        effort = float(charge["g_plus_q_kn"])
        cote_min = math.sqrt(effort / q_effectif)
        cote_adopte = arrondir_superieur(cote_min)
        resultats.append({
            "type": str(charge["type"]),
            "effort_kn": effort,
            "cote_minimale_m": cote_min,
            "cote_adoptee_m": cote_adopte,
            "contrainte_sol_utilisee_kpa": q_effectif,
        })
    return resultats
