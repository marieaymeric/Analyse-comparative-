from constantes import DOSSIER_SORTIE, FICHIER_CATALOGUE, FICHIER_MARCHE_LAGUNE, \
    FICHIER_BAOBAB, FICHIER_COMPTOIR, FICHIER_HISTORIQUE, JOURNAL, noter
from chargement import charger_catalogue, charger_marche_lagune, charger_baobab, \
    charger_comptoir, charger_historique
from anomalies import detecter_anomalies_prix
from comparatif import construire_comparatif, exporter_comparatif_csv
from synthese import construire_synthese, ecrire_synthese
from panier import calculer_panier
from historique import construire_index_historique, analyser_black_friday
from complexite import mesurer_complexite


def main():
    print("Chargement des fichiers...")
    catalogue = charger_catalogue(FICHIER_CATALOGUE)
    lignes_historique = charger_historique(FICHIER_HISTORIQUE)
    index_historique = construire_index_historique(lignes_historique)

    enseignes_donnees = {
        "Marché Lagune": charger_marche_lagune(FICHIER_MARCHE_LAGUNE, catalogue),
        "Baobab Shop": charger_baobab(FICHIER_BAOBAB, catalogue),
        "Comptoir Ivoire": charger_comptoir(FICHIER_COMPTOIR, catalogue),
    }

    print("Détection des prix anormaux par rapport à l'historique...")
    detecter_anomalies_prix(enseignes_donnees, index_historique)

    # Produits jamais proposés par une enseigne : utile pour le journal
    for nom_enseigne, produits in enseignes_donnees.items():
        produits_manquants = [p["produit_id"] for p in catalogue if p["produit_id"] not in produits]
        if produits_manquants:
            noter(f"[{nom_enseigne}] ne propose pas les produits suivants : "
                  f"{', '.join(produits_manquants)}.")

    print("Construction du comparatif de prix ...")
    lignes_comparatif = construire_comparatif(catalogue, enseignes_donnees)
    exporter_comparatif_csv(lignes_comparatif, f"{DOSSIER_SORTIE}/comparatif_prix.csv")

    print("Construction de la synthèse...")
    nb_moins_cher, ecart_moyen, top3 = construire_synthese(lignes_comparatif)
    texte_synthese = ecrire_synthese(
        f"{DOSSIER_SORTIE}/synthese.txt", nb_moins_cher, ecart_moyen, top3, len(lignes_comparatif)
    )

    print("Calcul du panier de rentrée ...")
    calculer_panier(catalogue, enseignes_donnees, f"{DOSSIER_SORTIE}/panier.txt")

    print("Analyse de l'historique des prix ...")
    analyser_black_friday(index_historique, f"{DOSSIER_SORTIE}/historique_black_friday.txt")

    print("Mesure de complexité...")
    mesurer_complexite(lignes_historique, catalogue, f"{DOSSIER_SORTIE}/complexite.txt")

    # Journal de nettoyage (étape 2), écrit en dernier pour tout rassembler
    with open(f"{DOSSIER_SORTIE}/journal_nettoyage.txt", "w", encoding="utf-8") as f:
        f.write(f"JOURNAL DE NETTOYAGE ({len(JOURNAL)} remarques)\n")
        f.write("=" * 40 + "\n\n")
        f.write("\n".join(JOURNAL) + "\n")

    print("\nTerminé. Fichiers générés dans le dossier output/ :")
    print("  - comparatif_prix.csv")
    print("  - synthese.txt")
    print("  - panier.txt")
    print("  - historique_black_friday.txt")
    print("  - complexite.txt")
    print("  - journal_nettoyage.txt")
    print()
    print(texte_synthese)


if __name__ == "__main__":
    main()