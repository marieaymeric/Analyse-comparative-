# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

DOSSIER_DONNEES = "data"
DOSSIER_SORTIE = "output"

FICHIER_CATALOGUE = f"{DOSSIER_DONNEES}/catalogue_reference.csv"
FICHIER_MARCHE_LAGUNE = f"{DOSSIER_DONNEES}/marche_lagune.csv"
FICHIER_BAOBAB = f"{DOSSIER_DONNEES}/baobab_shop.json"
FICHIER_COMPTOIR = f"{DOSSIER_DONNEES}/comptoir_ivoire.xlsx"
FICHIER_HISTORIQUE = f"{DOSSIER_DONNEES}/historique_prix.csv"

ENSEIGNES = ["Marché Lagune", "Baobab Shop", "Comptoir Ivoire"]

# Panier de rentrée demandé dans l'énoncé (étape 6)
PANIER = [
    ("P04", "Tecno Spark 20", 1),
    ("P12", "Lenovo IdeaPad 3", 1),
    ("P14", "Clé USB SanDisk", 2),
    ("P15", "Disque dur Seagate", 1),
    ("P28", "Micro-ondes Samsung", 1),
]

# Semaine du Black Friday (étape 7)
DATE_DEBUT_BF = "2025-11-24"
DATE_FIN_BF = "2025-11-30"

# Petit dictionnaire de traduction anglais -> français pour les libellés de
# Baobab Shop, qui décrit certains articles en anglais (Fridge, Blender...)
# alors que le catalogue de référence est en français. Sans cette étape, le
# rapprochement (étape 3) échoue sur l'électroménager.
TRADUCTIONS = {
    "FRIDGE": "REFRIGERATEUR", "REFRIGERATOR": "REFRIGERATEUR", "FRIGO": "REFRIGERATEUR",
    "MONITOR": "ECRAN", "SCREEN": "ECRAN",
    "BLENDER": "MIXEUR",
    "IRON": "FER REPASSER",
    "MICROWAVE": "MICRO ONDES",
    "KETTLE": "BOUILLOIRE ELECTRIQUE",
    "CONDITIONER": "CLIMATISEUR", "CLIM": "CLIMATISEUR",
    "FAN": "VENTILATEUR", "VENTILO": "VENTILATEUR",
    "ROUTER": "ROUTEUR",
    "LAPTOP": "PORTABLE",
    "PRINTER": "IMPRIMANTE",
    "MOUSE": "SOURIS",
    "WIRELESS": "SANS FIL",
    "EXPANSION": "DISQUE DUR EXTERNE",
    "DRIVE": "DISQUE DUR",
    "FREEZER": "CONGELATEUR",
}


# ---------------------------------------------------------------------------
# Journal global de nettoyage (étape 2)
# ---------------------------------------------------------------------------
# Chaque fonction de nettoyage y ajoute une ligne par problème rencontré.
# Il est écrit dans output/journal_nettoyage.txt par analyse.py.

JOURNAL = []


def noter(message):
    """Ajoute une ligne au journal de nettoyage et l'affiche à l'écran."""
    JOURNAL.append(message)