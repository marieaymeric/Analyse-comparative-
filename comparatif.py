import csv

from constantes import ENSEIGNES


def construire_comparatif(catalogue, enseignes_donnees):
    """Construit la liste des lignes du comparatif : un produit par ligne,
    uniquement les produits disponibles dans au moins deux enseignes."""
    lignes = []

    for produit in catalogue:
        produit_id = produit["produit_id"]

        prix_par_enseigne = {}
        for nom_enseigne in ENSEIGNES:
            infos = enseignes_donnees[nom_enseigne].get(produit_id)
            # Un produit en rupture ou sans prix exploitable n'est pas retenu
            # (consigne explicite de l'énoncé).
            if infos is not None and infos["disponible"] and infos["prix"] is not None:
                prix_par_enseigne[nom_enseigne] = infos["prix"]

        if len(prix_par_enseigne) < 2:
            continue  # pas de comparaison possible

        moins_cher_enseigne = min(prix_par_enseigne, key=prix_par_enseigne.get)
        prix_min = prix_par_enseigne[moins_cher_enseigne]
        prix_max = max(prix_par_enseigne.values())
        ecart_fcfa = prix_max - prix_min
        ecart_pct = (ecart_fcfa / prix_min * 100) if prix_min else 0

        lignes.append({
            "produit_id": produit_id,
            "nom": produit["nom"],
            "categorie": produit["categorie"],
            "prix_marche_lagune": prix_par_enseigne.get("Marché Lagune"),
            "prix_baobab_shop": prix_par_enseigne.get("Baobab Shop"),
            "prix_comptoir_ivoire": prix_par_enseigne.get("Comptoir Ivoire"),
            "moins_cher": moins_cher_enseigne,
            "prix_min": prix_min,
            "ecart_fcfa": ecart_fcfa,
            "ecart_pct": round(ecart_pct, 1),
        })

    return lignes


def exporter_comparatif_csv(lignes_comparatif, chemin):
    colonnes = [
        "produit_id", "nom", "categorie",
        "prix_marche_lagune", "prix_baobab_shop", "prix_comptoir_ivoire",
        "moins_cher", "prix_min", "ecart_fcfa", "ecart_pct",
    ]
    with open(chemin, "w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes)
        ecrivain.writeheader()
        ecrivain.writerows(lignes_comparatif)