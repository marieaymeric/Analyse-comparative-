from constantes import noter
from historique import prix_moyen

# Un prix est jugé "anormal" s'il s'écarte de plus de 50% du prix moyen
# historique de cette enseigne pour ce produit.
SEUIL_ECART = 0.50


def detecter_anomalies_prix(enseignes_donnees, index_historique):
    """Parcourt les prix du jour de chaque enseigne et les compare à leur
    prix moyen historique. Journalise les écarts supérieurs à SEUIL_ECART."""
    for nom_enseigne, produits in enseignes_donnees.items():
        for produit_id, infos in produits.items():
            prix_jour = infos["prix"]
            if prix_jour is None:
                continue  # déjà signalé lors du chargement

            moyenne = prix_moyen(index_historique, nom_enseigne, produit_id)
            if moyenne is None or moyenne == 0:
                continue  # pas d'historique pour ce couple (enseigne, produit)

            ecart = (prix_jour - moyenne) / moyenne
            if abs(ecart) > SEUIL_ECART:
                sens = "supérieur" if ecart > 0 else "inférieur"
                noter(
                    f"[{nom_enseigne}] {produit_id} ({infos['libelle']}) : prix du "
                    f"jour {prix_jour:,.0f} FCFA {sens} de {abs(ecart) * 100:.0f}% au "
                    f"prix moyen historique ({moyenne:,.0f} FCFA) -> à vérifier, "
                    f"prix conservé tel quel."
                )