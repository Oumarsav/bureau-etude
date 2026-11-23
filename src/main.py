"""Point d'entrée : menu console du projet Bureau d'études."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime

from .elements import Projet, saisir_projet
from .charges import calculer_poids_propre, descente_de_charges
from .predimensionnement import predimensionner_poteaux, predimensionner_semelles
from .devis import generer_devis, exporter_bordereau

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_DONNEES = RACINE / "donnees"
DOSSIER_RAPPORTS = RACINE / "rapports"


def afficher_tableau(titre: str, lignes: list[dict], colonnes: list[tuple[str, str, str]]) -> None:
    """Affiche une petite table alignée dans le terminal."""
    print(f"\n--- {titre} ---")
    entetes = [c[0] for c in colonnes]
    largeurs = [max(len(entetes[i]), *(len(str(l.get(colonnes[i][1], ""))) for l in lignes)) for i in range(len(colonnes))]
    print(" | ".join(entetes[i].ljust(largeurs[i]) for i in range(len(entetes))))
    print("-+-".join("-" * largeur for largeur in largeurs))
    for ligne in lignes:
        cellules = []
        for i, (_, cle, format_type) in enumerate(colonnes):
            valeur = ligne.get(cle, "")
            if isinstance(valeur, (float, int)) and format_type == "nombre":
                valeur = f"{valeur:.3f}"
            cellules.append(str(valeur).ljust(largeurs[i]))
        print(" | ".join(cellules))


def afficher_menu() -> None:
    print("\n" + "=" * 58)
    print("       BUREAU D'ÉTUDES — PROJET 1")
    print("       Cahier des charges et prédimensionnement")
    print("=" * 58)
    print("1. Saisir un nouveau projet")
    print("2. Charger un projet JSON")
    print("3. Calculer le poids propre")
    print("4. Effectuer la descente de charges")
    print("5. Prédimensionner les poteaux et les semelles")
    print("6. Générer le devis estimatif")
    print("7. Exporter un rapport")
    print("8. Quitter")


def exporter_rapport(projet: Projet) -> Path:
    """Produit un rapport texte avec les données et résultats calculés."""
    poids = calculer_poids_propre(projet)
    charges = descente_de_charges(projet)
    poteaux = predimensionner_poteaux(projet)
    semelles = predimensionner_semelles(projet)
    devis = generer_devis(projet)
    date = datetime.now().strftime("%d/%m/%Y à %H:%M")
    lignes = [
        "RAPPORT — BUREAU D'ÉTUDES", "=" * 58,
        f"Projet : {projet.nom}", f"Date d'édition : {date}", "",
        "1. DONNÉES DU PROJET", "-" * 30,
        f"Surface de dalle : {projet.surface_dalle_m2:.2f} m²",
        f"Épaisseur : {projet.epaisseur_dalle_m:.3f} m",
        f"Nombre de niveaux : {projet.nombre_niveaux}",
        f"Charges permanentes complémentaires : {projet.charges_permanentes_kn_m2:.2f} kN/m²",
        f"Charges d'exploitation : {projet.charges_exploitation_kn_m2:.2f} kN/m²", "",
        "2. POIDS PROPRE", "-" * 30,
    ]
    lignes += [f"{cle.replace('_', ' ')} : {valeur:.3f}" for cle, valeur in poids.items()]
    lignes += ["", "3. DESCENTE DE CHARGES SIMPLIFIÉE", "-" * 30]
    for c in charges:
        lignes.append(f"{c['type']} : surface d'influence = {c['surface_influence_m2']:.2f} m² ; N = {c['effort_kn']:.2f} kN")
    lignes += ["", "4. PRÉDIMENSIONNEMENT DES POTEAUX", "-" * 30]
    for p in poteaux:
        lignes.append(f"{p['type']} : A_min = {p['aire_minimale_m2']:.4f} m² ; côté théorique = {p['cote_theorique_m']:.3f} m ; côté adopté = {p['cote_adopte_m']:.2f} m")
    lignes += ["", "5. PRÉDIMENSIONNEMENT DES SEMELLES", "-" * 30]
    for s in semelles:
        lignes.append(f"{s['type']} : B_min = {s['cote_minimale_m']:.3f} m ; côté adopté = {s['cote_adoptee_m']:.2f} m")
    lignes += ["", "6. DEVIS ESTIMATIF", "-" * 30]
    for d in devis:
        lignes.append(f"{d['designation']} : {float(d['montant_fcfa']):,.0f} FCFA")
    lignes += ["", "7. HYPOTHÈSES ET LIMITES", "-" * 30,
        "Calculs simplifiés à but pédagogique uniquement.",
        "Le modèle ne vérifie pas les combinaisons réglementaires, le flambement,",
        "le ferraillage, le poinçonnement, le glissement, le tassement ni les plans.",
        "Les dimensions doivent être vérifiées par un ingénieur structure avant tout usage réel.", ""]
    DOSSIER_RAPPORTS.mkdir(parents=True, exist_ok=True)
    chemin = DOSSIER_RAPPORTS / "rapport_projet.txt"
    chemin.write_text("\n".join(lignes), encoding="utf-8")
    exporter_bordereau(devis, DOSSIER_RAPPORTS / "bordereau_devis.csv")
    return chemin


def main() -> None:
    projet: Projet | None = None
    while True:
        afficher_menu()
        choix = input("Votre choix (1-8) : ").strip()
        try:
            if choix == "1":
                projet = saisir_projet()
                chemin = DOSSIER_DONNEES / "mon_projet.json"
                projet.enregistrer(chemin)
                print(f"Projet enregistré : {chemin}")
            elif choix == "2":
                chemin_saisi = input("Chemin du fichier JSON [donnees/projet_exemple.json] : ").strip()
                chemin = Path(chemin_saisi) if chemin_saisi else DOSSIER_DONNEES / "projet_exemple.json"
                if not chemin.is_absolute():
                    chemin = RACINE / chemin
                projet = Projet.charger(chemin)
                print(f"Projet « {projet.nom} » chargé avec succès.")
            elif choix in {"3", "4", "5", "6", "7"}:
                if projet is None:
                    print("Veuillez d'abord saisir un projet (1) ou charger un projet (2).")
                    continue
                if choix == "3":
                    resultats = calculer_poids_propre(projet)
                    for nom, valeur in resultats.items():
                        print(f"{nom.replace('_', ' ')} : {valeur:.3f}")
                elif choix == "4":
                    afficher_tableau("DESCENTE DE CHARGES", descente_de_charges(projet), [
                        ("Poteau", "type", "texte"), ("Surface (m²)", "surface_influence_m2", "nombre"), ("Effort N (kN)", "effort_kn", "nombre")])
                elif choix == "5":
                    afficher_tableau("POTEAUX", predimensionner_poteaux(projet), [
                        ("Type", "type", "texte"), ("N (kN)", "effort_kn", "nombre"), ("A min (m²)", "aire_minimale_m2", "nombre"), ("Côté adopté (m)", "cote_adopte_m", "nombre")])
                    afficher_tableau("SEMELLES", predimensionner_semelles(projet), [
                        ("Type", "type", "texte"), ("N (kN)", "effort_kn", "nombre"), ("B min (m)", "cote_minimale_m", "nombre"), ("B adopté (m)", "cote_adoptee_m", "nombre")])
                elif choix == "6":
                    devis = generer_devis(projet)
                    afficher_tableau("DEVIS ESTIMATIF", devis, [
                        ("Désignation", "designation", "texte"), ("Quantité", "quantite", "nombre"), ("PU (FCFA)", "prix_unitaire_fcfa", "nombre"), ("Montant (FCFA)", "montant_fcfa", "nombre")])
                    exporter_bordereau(devis, DOSSIER_RAPPORTS / "bordereau_devis.csv")
                    print("Bordereau enregistré dans rapports/bordereau_devis.csv")
                else:
                    chemin = exporter_rapport(projet)
                    print(f"Rapport créé : {chemin}")
                    print(f"Bordereau créé : {DOSSIER_RAPPORTS / 'bordereau_devis.csv'}")
            elif choix == "8":
                print("Fin du programme. Bonne continuation !")
                break
            else:
                print("Choix invalide. Entrez un nombre de 1 à 8.")
        except (ValueError, OSError, KeyError) as erreur:
            print(f"Impossible d'effectuer cette opération : {erreur}")


if __name__ == "__main__":
    main()
