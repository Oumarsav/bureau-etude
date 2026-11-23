"""Tests unitaires des calculs de charges et du prédimensionnement."""
import math
import unittest
from src.elements import Projet
from src.charges import calculer_poids_propre, descente_de_charges
from src.predimensionnement import predimensionner_poteaux, predimensionner_semelles


class TestCalculs(unittest.TestCase):
    def setUp(self):
        self.projet = Projet()

    def test_poids_propre_dalle(self):
        resultat = calculer_poids_propre(self.projet)
        self.assertAlmostEqual(resultat["poids_dalle_kn_m2"], 3.75)
        self.assertAlmostEqual(resultat["charge_totale_service_kn_m2"], 7.25)
        self.assertAlmostEqual(resultat["poids_total_dalle_kn"], 375.0)

    def test_descente_charges(self):
        resultat = descente_de_charges(self.projet)
        self.assertEqual(len(resultat), 3)
        self.assertAlmostEqual(resultat[0]["g_plus_q_kn"], 87.0)
        self.assertAlmostEqual(resultat[1]["g_plus_q_kn"], 174.0)
        self.assertAlmostEqual(resultat[2]["g_plus_q_kn"], 290.0)
        self.assertGreater(resultat[0]["effort_kn"], resultat[0]["g_plus_q_kn"])

    def test_semelle_est_positive_et_arrondie(self):
        resultat = predimensionner_semelles(self.projet)
        for semelle in resultat:
            self.assertGreaterEqual(semelle["cote_adoptee_m"], semelle["cote_minimale_m"])
            self.assertTrue(math.isclose(semelle["cote_adoptee_m"] / 0.05,
                                         round(semelle["cote_adoptee_m"] / 0.05)))

    def test_poteau_minimum_pedagogique(self):
        resultat = predimensionner_poteaux(self.projet)
        for poteau in resultat:
            self.assertGreaterEqual(poteau["cote_adopte_m"], 0.20)

    def test_rejette_surface_nulle(self):
        self.projet.surface_dalle_m2 = 0
        with self.assertRaises(ValueError):
            calculer_poids_propre(self.projet)


if __name__ == "__main__":
    unittest.main()
