from constantes import ENSEIGNES, PANIER


def calculer_panier(catalogue, enseignes_donnees, chemin):
    """Calcule le coût du panier de rentrée dans chaque enseigne, puis en
    panier mixte (chaque article pris là où il est le moins cher). Écrit le
    détail dans un fichier texte."""
    lignes_texte = []
    lignes_texte.append("PANIER DE RENTRÉE")
    lignes_texte.append("=" * 40)
    lignes_texte.append("Contenu : " + ", ".join(f"{qte}x {nom}" for _, nom, qte in PANIER))
    lignes_texte.append("")

    # --- Coût du panier complet dans chaque enseigne ---
    total_panier_mixte = 0

    for enseigne in ENSEIGNES:
        total_enseigne = 0
        articles_manquants = []

        for produit_id, nom_produit, quantite in PANIER:
            infos = enseignes_donnees[enseigne].get(produit_id)
            if infos is None or not infos["disponible"] or infos["prix"] is None:
                articles_manquants.append(nom_produit)
                continue
            total_enseigne += infos["prix"] * quantite

        if articles_manquants:
            lignes_texte.append(
                f"{enseigne} : panier incomplet, indisponible(s) : "
                f"{', '.join(articles_manquants)}."
            )
        else:
            lignes_texte.append(f"{enseigne} : {total_enseigne:,.0f} FCFA (panier complet)")

    lignes_texte.append("")

    # --- Panier mixte : chaque article pris là où il est le moins cher ---
    lignes_texte.append("Panier mixte (chaque article acheté là où il est le moins cher) :")
    detail_mixte_impossible = []

    for produit_id, nom_produit, quantite in PANIER:
        prix_disponibles = {}
        for enseigne in ENSEIGNES:
            infos = enseignes_donnees[enseigne].get(produit_id)
            if infos is not None and infos["disponible"] and infos["prix"] is not None:
                prix_disponibles[enseigne] = infos["prix"]

        if not prix_disponibles:
            detail_mixte_impossible.append(nom_produit)
            continue

        meilleure_enseigne = min(prix_disponibles, key=prix_disponibles.get)
        prix_unitaire = prix_disponibles[meilleure_enseigne]
        sous_total = prix_unitaire * quantite
        total_panier_mixte += sous_total
        lignes_texte.append(
            f"  - {quantite}x {nom_produit} chez {meilleure_enseigne} : "
            f"{prix_unitaire:,.0f} FCFA/unité -> {sous_total:,.0f} FCFA"
        )

    if detail_mixte_impossible:
        lignes_texte.append(
            f"  Articles introuvables partout : {', '.join(detail_mixte_impossible)}"
        )

    lignes_texte.append(f"  TOTAL panier mixte : {total_panier_mixte:,.0f} FCFA")

    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_texte) + "\n")