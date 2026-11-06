import re
import unicodedata

from constantes import TRADUCTIONS


def normaliser_texte(texte):
    """Met un libellé en majuscules, sans accents ni ponctuation, et traduit
    quelques mots anglais courants. Sert à comparer des noms de produits
    écrits différemment d'une enseigne à l'autre."""
    texte = str(texte).upper()
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    texte = re.sub(r"[^A-Z0-9]+", " ", texte)
    for mot_en, mot_fr in TRADUCTIONS.items():
        texte = re.sub(r"\b" + mot_en + r"\b", mot_fr, texte)
    return re.sub(r"\s+", " ", texte).strip()


def nettoyer_prix(texte_prix):
    """Transforme un prix écrit en texte ("102 900 FCFA", "Prix sur demande",
    "", 109400...) en entier FCFA, ou None si le prix est inexploitable.
    Retourne (valeur, motif_erreur)."""
    if texte_prix is None:
        return None, "valeur absente"
    texte_prix = str(texte_prix).strip()
    if texte_prix == "":
        return None, "prix vide"
    chiffres = re.sub(r"[^\d]", "", texte_prix)
    if chiffres == "":
        return None, f"prix non numérique ({texte_prix!r})"
    return int(chiffres), None


def nettoyer_note(texte_note):
    """Convertit une note écrite à la française ("4,2") en flottant (4.2)."""
    if texte_note is None or str(texte_note).strip() == "":
        return None
    try:
        return float(str(texte_note).replace(",", "."))
    except ValueError:
        return None