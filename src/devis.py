"""Création d'un bordereau et d'un devis simplifié."""
from __future__ import annotations
import csv
from pathlib import Path
from .elements import Projet
from .predimensionnement import predimensionner_poteaux, predimensionner_semelles


def generer_devis(projet: Projet) -> list[dict[str, float | str]]:
    """Estime quelques quantités de béton et de coffrage.

    Les quantités sont indicatives : poteaux sur tous les niveaux et semelles
    carrées d'épaisseur forfaitaire 0,30 m. L'acier est laissé à zéro car aucun
    plan de ferraillage n'est fourni dans le sujet.
    """
    poteaux = predimensionner_poteaux(projet)
    semelles = predimensionner_semelles(projet)
    volume_poteaux = sum(float(p["cote_adopte_m"]) ** 2 * 3.0 * projet.nombre_niveaux for p in poteaux)
    volume_semelles = sum(float(s["cote_adoptee_m"]) ** 2 * 0.30 for s in semelles)
    volume_beton = volume_poteaux + volume_semelles
    surface_coffrage = sum(4 * float(p["cote_adopte_m"]) * 3.0 * projet.nombre_niveaux for p in poteaux)
    lignes = [
        {"designation": "Béton poteaux et semelles (m³)", "quantite": volume_beton,
         "prix_unitaire_fcfa": projet.cout_beton_m3_fcfa,
         "montant_fcfa": volume_beton * projet.cout_beton_m3_fcfa},
        {"designation": "Coffrage des poteaux (m²)", "quantite": surface_coffrage,
         "prix_unitaire_fcfa": projet.cout_coffrage_m2_fcfa,
         "montant_fcfa": surface_coffrage * projet.cout_coffrage_m2_fcfa},
        {"designation": "Acier (quantité à déterminer par étude de ferraillage)", "quantite": 0.0,
         "prix_unitaire_fcfa": projet.cout_acier_kg_fcfa, "montant_fcfa": 0.0},
    ]
    sous_total = sum(float(l["montant_fcfa"]) for l in lignes)
    imprevus = sous_total * projet.taux_imprevus
    lignes.append({"designation": "Imprévus", "quantite": projet.taux_imprevus,
                   "prix_unitaire_fcfa": sous_total, "montant_fcfa": imprevus})
    lignes.append({"designation": "TOTAL ESTIMATIF", "quantite": 1.0,
                   "prix_unitaire_fcfa": sous_total + imprevus,
                   "montant_fcfa": sous_total + imprevus})
    return lignes


def exporter_bordereau(lignes: list[dict[str, float | str]], chemin: str | Path) -> None:
    destination = Path(chemin)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="", encoding="utf-8-sig") as fichier:
        writer = csv.DictWriter(fichier, fieldnames=["designation", "quantite", "prix_unitaire_fcfa", "montant_fcfa"])
        writer.writeheader()
        writer.writerows(lignes)
