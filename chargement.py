import csv
import json

import openpyxl

from constantes import noter
from nettoyage_texte import normaliser_texte, nettoyer_prix, nettoyer_note


def charger_catalogue(chemin):
    """Charge catalogue_reference.csv -> liste de dicts, avec un libellé
    normalisé pré-calculé pour le rapprochement (étape 3)."""
    with open(chemin, encoding="utf-8") as f:
        catalogue = list(csv.DictReader(f))
    for produit in catalogue:
        produit["texte_normalise"] = normaliser_texte(
            produit["nom"] + " " + produit["marque"]
        )
    return catalogue


def trouver_produit(catalogue, libelle):
    """Rapproche un libellé d'enseigne avec un produit_id du catalogue, en
    comptant le nombre de mots en commun entre les deux libellés normalisés.
    Retourne (produit, score_du_meilleur, score_du_deuxieme) pour pouvoir
    détecter les correspondances douteuses dans le journal."""
    mots_libelle = set(normaliser_texte(libelle).split())
    scores = []
    for produit in catalogue:
        mots_catalogue = set(produit["texte_normalise"].split())
        score = len(mots_libelle & mots_catalogue)
        scores.append((score, produit))
    scores.sort(key=lambda t: t[0], reverse=True)
    meilleur_score, meilleur_produit = scores[0]
    deuxieme_score = scores[1][0] if len(scores) > 1 else 0
    return meilleur_produit, meilleur_score, deuxieme_score


def rapprocher(catalogue, libelle, source, reference):
    """Applique trouver_produit() et journalise les correspondances fragiles
    (score trop faible, ou égalité avec un deuxième produit)."""
    produit, score, score2 = trouver_produit(catalogue, libelle)
    if score == 0:
        noter(f"[{source}] '{libelle}' ({reference}) : aucune correspondance "
              f"trouvée dans le catalogue, article ignoré.")
        return None
    if score < 2 or score == score2:
        noter(f"[{source}] '{libelle}' ({reference}) : correspondance "
              f"incertaine avec {produit['produit_id']} ({produit['nom']}) "
              f"[score={score}, 2e meilleur score={score2}] -> conservée mais à vérifier.")
    return produit["produit_id"]


def charger_marche_lagune(chemin, catalogue):
    """Charge marche_lagune.csv (encodage avec BOM, séparateur ';').
    Nettoie : doublons de référence, espaces inutiles, prix textuels,
    disponibilité. Retourne un dict produit_id -> infos."""
    with open(chemin, encoding="utf-8-sig", newline="") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))

    resultats = {}
    references_vues = set()

    for ligne in lignes:
        ref = ligne["reference"].strip()
        designation_brute = ligne["designation"]
        designation = designation_brute.strip()

        if designation_brute != designation:
            noter(f"[Marché Lagune] '{designation_brute}' ({ref}) : espaces "
                  f"superflus en début/fin de libellé, corrigés.")

        if ref in references_vues:
            noter(f"[Marché Lagune] référence {ref} en double dans le "
                  f"fichier, deuxième occurrence ignorée.")
            continue
        references_vues.add(ref)

        produit_id = rapprocher(catalogue, designation, "Marché Lagune", ref)
        if produit_id is None:
            continue

        prix, erreur_prix = nettoyer_prix(ligne["prix"])
        if erreur_prix:
            noter(f"[Marché Lagune] {ref} ({designation}) : {erreur_prix}, "
                  f"prix écarté du comparatif.")

        ancien_prix, _ = nettoyer_prix(ligne["ancien_prix"])
        disponible = ligne["disponibilite"].strip() != "Rupture"

        resultats[produit_id] = {
            "reference": ref,
            "libelle": designation,
            "prix": prix,          # le prix affiché inclut déjà la livraison
            "ancien_prix": ancien_prix,
            "disponible": disponible,
            "disponibilite_texte": ligne["disponibilite"].strip(),
            "note": nettoyer_note(ligne["note_clients"]),
            "nb_avis": int(ligne["nb_avis"]) if ligne["nb_avis"].strip().isdigit() else None,
        }

    return resultats


def charger_baobab(chemin, catalogue):
    """Charge baobab_shop.json. Nettoie : prix manquant (amount=null),
    rupture de stock. Le client paie amount + delivery_fee."""
    with open(chemin, encoding="utf-8") as f:
        contenu = json.load(f)

    resultats = {}
    for article in contenu["items"]:
        sku = article["sku"]
        titre = article["title"]

        produit_id = rapprocher(catalogue, titre, "Baobab Shop", sku)
        if produit_id is None:
            continue

        montant = article["pricing"]["amount"]
        livraison = article["pricing"].get("delivery_fee", 0) or 0

        if montant is None:
            noter(f"[Baobab Shop] {sku} ({titre}) : prix manquant (amount=null), "
                  f"article écarté du comparatif.")
            prix_total = None
        else:
            prix_total = montant + livraison

        disponible = article["stock"] > 0
        if not disponible:
            noter(f"[Baobab Shop] {sku} ({titre}) : stock à 0, article en rupture.")

        resultats[produit_id] = {
            "reference": sku,
            "libelle": titre,
            "prix": prix_total,
            "ancien_prix": None,
            "disponible": disponible,
            "disponibilite_texte": "En stock" if disponible else "Rupture",
            "note": article["rating"]["average"],
            "nb_avis": article["rating"]["count"],
        }

    return resultats


def charger_comptoir(chemin, catalogue):
    """Charge comptoir_ivoire.xlsx (feuille 'Tarifs octobre 2026') : titre en
    ligne 1, en-têtes en ligne 3, données à partir de la ligne 4. Nettoie :
    prix catalogue parfois écrit en texte, remise à appliquer, article non
    disponible en rayon. Le client paie prix_catalogue * (1 - remise%)."""
    classeur = openpyxl.load_workbook(chemin, data_only=True)
    feuille = classeur.active

    resultats = {}
    for ligne in feuille.iter_rows(min_row=4, values_only=True):
        code = ligne[0]
        if code is None:          # lignes vides en bas de feuille
            continue

        article, rayon, prix_catalogue, remise, quantite, _date_maj = ligne[1:7]

        produit_id = rapprocher(catalogue, article, "Comptoir Ivoire", code)
        if produit_id is None:
            continue

        prix_brut, erreur_prix = nettoyer_prix(prix_catalogue)
        if erreur_prix:
            noter(f"[Comptoir Ivoire] {code} ({article}) : {erreur_prix}, "
                  f"prix écarté du comparatif.")
        elif not isinstance(prix_catalogue, (int, float)):
            noter(f"[Comptoir Ivoire] {code} ({article}) : prix catalogue "
                  f"stocké en texte ('{prix_catalogue}') plutôt qu'en nombre, corrigé.")

        remise = remise or 0
        prix_final = round(prix_brut * (1 - remise / 100)) if prix_brut is not None else None

        quantite = quantite or 0
        disponible = quantite > 0
        if not disponible:
            noter(f"[Comptoir Ivoire] {code} ({article}) : quantité en rayon "
                  f"à 0, article en rupture.")

        resultats[produit_id] = {
            "reference": code,
            "libelle": article,
            "prix": prix_final,
            "ancien_prix": None,
            "disponible": disponible,
            "disponibilite_texte": "En stock" if disponible else "Rupture",
            "note": None,
            "nb_avis": None,
        }

    return resultats


def charger_historique(chemin):
    """Charge historique_prix.csv tel quel : une simple liste de lignes
    (date, source, produit_id, prix). Sert de base à l'étape 7 (historique)
    et à l'étape 8 (mesure de complexité)."""
    with open(chemin, encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        lignes = [
            (ligne["date"], ligne["source"], ligne["produit_id"], int(ligne["prix_fcfa"]))
            for ligne in lecteur
        ]
    return lignes