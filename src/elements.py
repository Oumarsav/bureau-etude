"""Modèles de données et fonctions de saisie/chargement du projet."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass
class Projet:
    """Données d'entrée principales d'un bâtiment simplifié."""
    nom: str = "Projet sans nom"
    surface_dalle_m2: float = 100.0
    epaisseur_dalle_m: float = 0.15
    poids_volumique_beton_kn_m3: float = 25.0
    charges_permanentes_kn_m2: float = 1.5
    charges_exploitation_kn_m2: float = 2.0
    nombre_niveaux: int = 2
    surface_influence_angle_m2: float = 6.0
    surface_influence_rive_m2: float = 12.0
    surface_influence_central_m2: float = 20.0
    contrainte_admissible_beton_kn_m2: float = 10000.0
    contrainte_admissible_sol_kpa: float = 200.0
    cout_beton_m3_fcfa: float = 85000.0
    cout_acier_kg_fcfa: float = 900.0
    cout_coffrage_m2_fcfa: float = 6500.0
    taux_imprevus: float = 0.05
    poteaux: list[dict[str, Any]] = field(default_factory=lambda: [
        {"type": "Angle", "surface_influence_m2": 6.0},
        {"type": "Rive", "surface_influence_m2": 12.0},
        {"type": "Central", "surface_influence_m2": 20.0},
    ])

    def valider(self) -> None:
        """Vérifie les valeurs avant les calculs."""
        valeurs_positives = {
            "surface de dalle": self.surface_dalle_m2,
            "épaisseur de dalle": self.epaisseur_dalle_m,
            "poids volumique du béton": self.poids_volumique_beton_kn_m3,
            "nombre de niveaux": self.nombre_niveaux,
            "contrainte admissible du béton": self.contrainte_admissible_beton_kn_m2,
            "contrainte admissible du sol": self.contrainte_admissible_sol_kpa,
        }
        for nom, valeur in valeurs_positives.items():
            if valeur <= 0:
                raise ValueError(f"La valeur « {nom} » doit être strictement positive.")
        for nom, valeur in (("charges permanentes", self.charges_permanentes_kn_m2),
                            ("charges d'exploitation", self.charges_exploitation_kn_m2),
                            ("taux d'imprévus", self.taux_imprevus)):
            if valeur < 0:
                raise ValueError(f"La valeur « {nom} » ne peut pas être négative.")
        if self.taux_imprevus > 1:
            raise ValueError("Le taux d'imprévus doit être saisi entre 0 et 1 (ex. 0.05 pour 5 %).")
        if not self.poteaux:
            raise ValueError("Le projet doit contenir au moins un type de poteau.")
        for poteau in self.poteaux:
            if float(poteau.get("surface_influence_m2", 0)) <= 0:
                raise ValueError("Chaque surface d'influence doit être positive.")

    def enregistrer(self, chemin: str | Path) -> None:
        """Enregistre les données du projet en JSON."""
        self.valider()
        destination = Path(chemin)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(asdict(self), ensure_ascii=False, indent=4), encoding="utf-8")

    @classmethod
    def charger(cls, chemin: str | Path) -> "Projet":
        """Charge un projet précédemment enregistré en JSON."""
        donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
        projet = cls(**donnees)
        projet.valider()
        return projet


def saisir_nombre(message: str, valeur_defaut: float, entier: bool = False) -> float | int:
    """Demande un nombre ; Entrée conserve la valeur proposée."""
    while True:
        brut = input(f"{message} [{valeur_defaut}] : ").strip().replace(",", ".")
        if not brut:
            return int(valeur_defaut) if entier else float(valeur_defaut)
        try:
            valeur = int(brut) if entier else float(brut)
            return valeur
        except ValueError:
            print("Saisie invalide : entrez un nombre, par exemple 12 ou 2.5.")


def saisir_projet() -> Projet:
    """Guide l'utilisateur pour créer un projet."""
    print("\n--- SAISIE D'UN NOUVEAU PROJET ---")
    nom = input("Nom du projet [Petit bâtiment] : ").strip() or "Petit bâtiment"
    p = Projet(nom=nom)
    p.surface_dalle_m2 = saisir_nombre("Surface de la dalle (m²)", p.surface_dalle_m2)
    p.epaisseur_dalle_m = saisir_nombre("Épaisseur de la dalle (m)", p.epaisseur_dalle_m)
    p.poids_volumique_beton_kn_m3 = saisir_nombre("Poids volumique du béton (kN/m³)", p.poids_volumique_beton_kn_m3)
    p.charges_permanentes_kn_m2 = saisir_nombre("Charges permanentes complémentaires (kN/m²)", p.charges_permanentes_kn_m2)
    p.charges_exploitation_kn_m2 = saisir_nombre("Charges d'exploitation (kN/m²)", p.charges_exploitation_kn_m2)
    p.nombre_niveaux = saisir_nombre("Nombre de niveaux", p.nombre_niveaux, entier=True)
    p.contrainte_admissible_beton_kn_m2 = saisir_nombre("Contrainte admissible béton (kN/m²)", p.contrainte_admissible_beton_kn_m2)
    p.contrainte_admissible_sol_kpa = saisir_nombre("Contrainte admissible du sol (kPa)", p.contrainte_admissible_sol_kpa)
    p.poteaux = []
    for nom_type, surface_defaut in (("Angle", 6.0), ("Rive", 12.0), ("Central", 20.0)):
        surface = saisir_nombre(f"Surface d'influence du poteau {nom_type} (m²)", surface_defaut)
        p.poteaux.append({"type": nom_type, "surface_influence_m2": surface})
    p.valider()
    return p
