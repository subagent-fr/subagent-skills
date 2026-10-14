"""Chaque recette, relue contre le contrat du serveur.

    python -m unittest discover -s tests -v
"""
import json
import re
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
CONTRAT = json.loads((RACINE / "contrat.json").read_text(encoding="utf-8"))
RECETTES = sorted(chemin.parent for chemin in RACINE.glob("*/SKILL.md"))
VOCABULAIRE = set(CONTRAT["vocabulaire"])


def lire(dossier):
    """(en-tête, corps) d'un SKILL.md : l'en-tête a deux champs, name et description."""
    texte = (dossier / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\nname: ([^\n]+)\ndescription: (\"(?:[^\"\\]|\\.)*\")\n---\n", texte)
    assert m, "%s : en-tête illisible" % dossier.name
    return {"name": m.group(1), "description": json.loads(m.group(2))}, texte[m.end():]


class Recettes(unittest.TestCase):
    def test_il_y_a_des_recettes(self):
        self.assertEqual(len(RECETTES), 7)

    def test_en_tete(self):
        for dossier in RECETTES:
            with self.subTest(dossier.name):
                entete, corps = lire(dossier)
                self.assertEqual(entete["name"], dossier.name)
                self.assertRegex(entete["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
                self.assertLessEqual(len(entete["name"]), 64)
                self.assertTrue(0 < len(entete["description"]) <= 1024, len(entete["description"]))
                self.assertNotRegex(entete["description"], r"[<>]")
                self.assertTrue(corps.strip().startswith("# "))

    def test_rien_n_est_nomme_hors_du_contrat(self):
        for dossier in RECETTES:
            with self.subTest(dossier.name):
                _, corps = lire(dossier)
                for mot in re.findall(r"`([a-z]+(?:_[a-z]+)+)`", corps):
                    self.assertIn(mot, VOCABULAIRE, "%s cite `%s`" % (dossier.name, mot))

    def test_aucun_gabarit_n_est_reste_ouvert(self):
        for dossier in RECETTES:
            with self.subTest(dossier.name):
                texte = (dossier / "SKILL.md").read_text(encoding="utf-8")
                self.assertNotRegex(texte, r"@@[a-z0-9_]+@@")
                self.assertIsNone(re.search(r"sak_[A-Za-z0-9]{6,}", texte.replace("sak_exemple_agent", "")))

    def test_le_contrat_couvre_les_outils_cites(self):
        cites = set()
        for dossier in RECETTES:
            _, corps = lire(dossier)
            cites |= set(re.findall(r"\*\*`([a-z_]+)`\*\* \(", corps))
        self.assertTrue(cites)
        self.assertLessEqual(cites, set(CONTRAT["outils"]))


if __name__ == "__main__":
    unittest.main()
