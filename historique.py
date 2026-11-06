from constantes import DATE_DEBUT_BF, DATE_FIN_BF, ENSEIGNES


def construire_index_historique(lignes_historique):

    index = {}
    for date, source, produit_id, prix in lignes_historique:
        cle = (source, produit_id)
        if cle not in index:
            index[cle] = []
        index[cle].append((date, prix))

    for cle in index:
        index[cle].sort()  # trie par date (le tuple commence par la date)

    return index


def prix_moyen(index_historique, source, produit_id):
   
    entrees = index_historique.get((source, produit_id))
    if not entrees:
        return None

    total = 0
    for date, prix in entrees:
        total += prix
    return total / len(entrees)


def analyser_black_friday(index_historique, chemin):

    lignes_texte = []
    lignes_texte.append("QUAND FALLAIT-IL ACHETER ? (semaine du Black Friday vs année)")
    lignes_texte.append("=" * 60)
    lignes_texte.append("")

    for enseigne in ENSEIGNES:
        prix_annee = []
        prix_bf = []

        for cle in index_historique:
            source, produit_id = cle
            if source != enseigne:
                continue
            for date, prix in index_historique[cle]:
                prix_annee.append(prix)
                if DATE_DEBUT_BF <= date <= DATE_FIN_BF:
                    prix_bf.append(prix)

        if len(prix_annee) == 0:
            lignes_texte.append(f"{enseigne} : aucune donnée dans l'historique.")
            continue

        moyenne_annee = sum(prix_annee) / len(prix_annee)

        if len(prix_bf) == 0:
            lignes_texte.append(
                f"{enseigne} : prix moyen annuel = {moyenne_annee:,.0f} FCFA, "
                f"mais aucune ligne d'historique pendant la semaine du Black Friday."
            )
            continue

        moyenne_bf = sum(prix_bf) / len(prix_bf)
        ecart_pct = (moyenne_bf - moyenne_annee) / moyenne_annee * 100

        if ecart_pct < 0:
            conseil = (f"{abs(ecart_pct):.1f}% moins cher que la moyenne de "
                       f"l'année : bon moment pour acheter.")
        else:
            conseil = (f"{ecart_pct:.1f}% plus cher que la moyenne de l'année : "
                       f"pas le meilleur moment.")

        lignes_texte.append(
            f"{enseigne} : prix moyen Black Friday = {moyenne_bf:,.0f} FCFA, "
            f"prix moyen annuel = {moyenne_annee:,.0f} FCFA -> {conseil}"
        )

    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_texte) + "\n")