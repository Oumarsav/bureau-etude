"""Calculs de poids propre et descente de charges simplifiée."""
from .elements import Projet


def calculer_poids_propre(projet: Projet) -> dict[str, float]:
    """Calcule le poids de la dalle et les charges surfaciques."""
    projet.valider()
    poids_volumique = projet.poids_volumique_beton_kn_m3
    poids_dalle_kn_m2 = projet.epaisseur_dalle_m * poids_volumique
    charge_permanente_totale = poids_dalle_kn_m2 + projet.charges_permanentes_kn_m2
    charge_totale_service = charge_permanente_totale + projet.charges_exploitation_kn_m2
    # Combinaison ELU pédagogique : 1,35 G + 1,50 Q.
    charge_elu = 1.35 * charge_permanente_totale + 1.50 * projet.charges_exploitation_kn_m2
    poids_total_dalle_kn = poids_dalle_kn_m2 * projet.surface_dalle_m2
    return {
        "poids_dalle_kn_m2": poids_dalle_kn_m2,
        "charge_permanente_totale_kn_m2": charge_permanente_totale,
        "charge_exploitation_kn_m2": projet.charges_exploitation_kn_m2,
        "charge_totale_service_kn_m2": charge_totale_service,
        "charge_elu_kn_m2": charge_elu,
        "poids_total_dalle_kn": poids_total_dalle_kn,
    }


def descente_de_charges(projet: Projet) -> list[dict[str, float | str]]:
    """Estime l'effort vertical transmis à chaque poteau type.

    Modèle volontairement simple : N_ELU = (1,35 G + 1,50 Q) × surface
    d'influence × nombre de niveaux. G+Q est aussi conservé pour les semelles.
    Il ne remplace pas une analyse de structure.
    """
    charges = calculer_poids_propre(projet)
    charge_service = charges["charge_totale_service_kn_m2"]
    charge_elu = charges["charge_elu_kn_m2"]
    resultats = []
    for poteau in projet.poteaux:
        surface = float(poteau["surface_influence_m2"])
        effort_service = charge_service * surface * projet.nombre_niveaux
        effort_elu = charge_elu * surface * projet.nombre_niveaux
        resultats.append({
            "type": str(poteau["type"]),
            "surface_influence_m2": surface,
            "effort_kn": effort_elu,
            "g_plus_q_kn": effort_service,
        })
    return resultats
