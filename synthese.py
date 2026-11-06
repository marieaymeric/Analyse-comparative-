from constantes import ENSEIGNES


def construire_synthese(lignes_comparatif):
 
    # 1. Nombre de fois où chaque enseigne est la moins chère
    nb_moins_cher = {enseigne: 0 for enseigne in ENSEIGNES}
    for ligne in lignes_comparatif:
        nb_moins_cher[ligne["moins_cher"]] += 1

    # 2. Écart moyen de chaque enseigne par rapport au prix le plus bas
    #    (uniquement sur les produits où l'enseigne est présente)
    sommes_ecarts = {enseigne: 0.0 for enseigne in ENSEIGNES}
    comptes = {enseigne: 0 for enseigne in ENSEIGNES}
    cles_prix = {
        "Marché Lagune": "prix_marche_lagune",
        "Baobab Shop": "prix_baobab_shop",
        "Comptoir Ivoire": "prix_comptoir_ivoire",
    }
    for ligne in lignes_comparatif:
        prix_min = ligne["prix_min"]
        for enseigne in ENSEIGNES:
            prix_enseigne = ligne[cles_prix[enseigne]]
            if prix_enseigne is None:
                continue
            ecart_pct = (prix_enseigne - prix_min) / prix_min * 100 if prix_min else 0
            sommes_ecarts[enseigne] += ecart_pct
            comptes[enseigne] += 1

    ecart_moyen = {
        enseigne: round(sommes_ecarts[enseigne] / comptes[enseigne], 1) if comptes[enseigne] else None
        for enseigne in ENSEIGNES
    }

    # 3. Les trois produits où il y a le plus à gagner à comparer (plus gros
    #    écart en FCFA entre le moins cher et le plus cher)
    top3 = sorted(lignes_comparatif, key=lambda l: l["ecart_fcfa"], reverse=True)[:3]

    return nb_moins_cher, ecart_moyen, top3


def ecrire_synthese(chemin, nb_moins_cher, ecart_moyen, top3, nb_produits_compares):
    """Écrit la synthèse dans un fichier texte lisible, et renvoie le même
    texte pour affichage dans le terminal."""
    lignes_texte = []
    lignes_texte.append("SYNTHÈSE DU COMPARATIF")
    lignes_texte.append("=" * 40)
    lignes_texte.append(f"Produits comparables (présents dans >= 2 enseignes) : {nb_produits_compares}")
    lignes_texte.append("")

    lignes_texte.append("Nombre de fois où chaque enseigne est la moins chère :")
    for enseigne in ENSEIGNES:
        lignes_texte.append(f"  - {enseigne} : {nb_moins_cher[enseigne]}")
    lignes_texte.append("")

    lignes_texte.append("Écart moyen par rapport au prix le plus bas (en %) :")
    for enseigne in ENSEIGNES:
        valeur = ecart_moyen[enseigne]
        texte_valeur = f"{valeur:.1f}%" if valeur is not None else "n/a (aucun produit comparable)"
        lignes_texte.append(f"  - {enseigne} : {texte_valeur}")
    lignes_texte.append("")

    lignes_texte.append("Les 3 produits où il y a le plus à gagner à comparer :")
    for ligne in top3:
        lignes_texte.append(
            f"  - {ligne['nom']} ({ligne['produit_id']}) : écart de "
            f"{ligne['ecart_fcfa']:,.0f} FCFA ({ligne['ecart_pct']}%), "
            f"moins cher chez {ligne['moins_cher']}."
        )

    texte_final = "\n".join(lignes_texte) + "\n"
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte_final)

    return texte_final