import time

from constantes import ENSEIGNES


def recherche_lineaire(lignes_historique, source, produit_id):
    """Reparcourt toute la liste brute pour trouver les lignes d'un couple
    (source, produit_id). O(n) à chaque appel."""
    return [
        (date, prix)
        for date, src, pid, prix in lignes_historique
        if src == source and pid == produit_id
    ]


def mesurer_complexite(lignes_historique, catalogue, chemin):
    """Chronomètre la recherche linéaire et la recherche indexée sur le même
    jeu de recherches (une par produit du catalogue, pour chaque enseigne),
    et écrit le résultat + l'explication dans un fichier texte."""

    recherches = [
        (enseigne, produit["produit_id"])
        for enseigne in ENSEIGNES
        for produit in catalogue
    ]
    nb_recherches = len(recherches)
    nb_lignes = len(lignes_historique)

    # --- Recherche linéaire : on reparcourt les 20 000+ lignes à chaque fois ---
    debut = time.perf_counter()
    for source, produit_id in recherches:
        recherche_lineaire(lignes_historique, source, produit_id)
    duree_lineaire = time.perf_counter() - debut

    # --- Recherche indexée : on construit l'index une fois, puis on consulte ---
    debut = time.perf_counter()
    index = {}
    for date, source, produit_id, prix in lignes_historique:
        index.setdefault((source, produit_id), []).append((date, prix))
    duree_construction_index = time.perf_counter() - debut

    debut = time.perf_counter()
    for source, produit_id in recherches:
        index.get((source, produit_id), [])
    duree_recherche_indexee = time.perf_counter() - debut

    duree_indexee_totale = duree_construction_index + duree_recherche_indexee

    lignes_texte = []
    lignes_texte.append("MESURE DE COMPLEXITÉ : RECHERCHE DANS L'HISTORIQUE")
    lignes_texte.append("=" * 55)
    lignes_texte.append(f"Taille de l'historique : {nb_lignes} lignes")
    lignes_texte.append(f"Nombre de recherches effectuées : {nb_recherches} "
                         f"({len(ENSEIGNES)} enseignes x {len(catalogue)} produits)")
    lignes_texte.append("")
    lignes_texte.append(
        f"Recherche linéaire (on reparcourt les {nb_lignes} lignes à chaque "
        f"recherche, complexité O(n) par recherche) :"
    )
    lignes_texte.append(f"  -> {duree_lineaire * 1000:.1f} ms pour les {nb_recherches} recherches")
    lignes_texte.append("")
    lignes_texte.append(
        "Recherche indexée (dictionnaire {(enseigne, produit_id): [...]} "
        "construit une seule fois, complexité O(n) une fois puis O(1) en "
        "moyenne par recherche) :"
    )
    lignes_texte.append(f"  -> {duree_construction_index * 1000:.1f} ms pour construire l'index")
    lignes_texte.append(f"  -> {duree_recherche_indexee * 1000:.1f} ms pour les {nb_recherches} recherches")
    lignes_texte.append(f"  -> {duree_indexee_totale * 1000:.1f} ms au total (construction + recherches)")
    lignes_texte.append("")

    if duree_lineaire > 0 and duree_indexee_totale > 0:
        facteur = duree_lineaire / duree_indexee_totale
        lignes_texte.append(f"Gain observé : environ {facteur:.1f}x plus rapide avec l'index.")
    lignes_texte.append("")

    lignes_texte.append("Explication des choix de structures de données :")
    lignes_texte.append(
        "- L'historique est chargé une seule fois comme une simple liste de "
        "tuples (date, source, produit_id, prix) : il n'y a pas de raison de "
        "le complexifier au chargement, on ne sait pas encore comment il sera "
        "consulté."
    )
    lignes_texte.append(
        "- Comme le programme doit ensuite faire BEAUCOUP de recherches dans "
        "cet historique (détection d'anomalies pour chaque produit de chaque "
        "enseigne, analyse Black Friday), reparcourir les 20 000+ lignes à "
        "chaque recherche (recherche linéaire, O(n) par recherche) devient "
        "coûteux dès qu'on fait plusieurs dizaines de recherches."
    )
    lignes_texte.append(
        "- On construit donc une seule fois un dictionnaire "
        "{(enseigne, produit_id): [(date, prix), ...]} (voir "
        "historique.construire_index_historique). Cette construction coûte "
        "O(n), mais une seule fois. Ensuite, chaque recherche par "
        "(enseigne, produit_id) est une simple consultation de dictionnaire, "
        "en moyenne en temps constant O(1), quel que soit le nombre de "
        "recherches effectuées ensuite."
    )
    lignes_texte.append(
        "- C'est ce choix (dictionnaire construit une fois, dans analyse.py, "
        "avant d'être réutilisé par anomalies.py et historique.py) qui "
        "explique le gain de temps mesuré ci-dessus."
    )

    with open(chemin, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_texte) + "\n")