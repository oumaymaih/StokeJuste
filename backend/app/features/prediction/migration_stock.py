from sqlalchemy import text

from .database import engine


# ==================================================
# MIGRATION : AJOUT DES INFORMATIONS DE COMMANDE
# ==================================================

def migrer_table_historique():

    print("=" * 60)
    print("MIGRATION DE LA TABLE PREDICTION_HISTORIQUE")
    print("=" * 60)

    # Ouvrir une transaction PostgreSQL
    # Validation automatique si toutes les opérations réussissent
    # Annulation automatique en cas d'erreur

    with engine.begin() as connexion:

        # ==================================================
        # 1. VERIFIER LA CONNEXION
        # ==================================================

        base = connexion.execute(
            text("SELECT current_database()")
        ).scalar()

        print("\nBase de données :", base)

        # ==================================================
        # 2. COMPTER LES PREDICTIONS EXISTANTES
        # ==================================================

        nombre_avant = connexion.execute(
            text("""
                SELECT COUNT(*)
                FROM prediction_historique;
            """)
        ).scalar()

        print("Nombre de prédictions avant :", nombre_avant)

        # ==================================================
        # 3. AJOUTER LE STOCK DISPONIBLE
        # ==================================================

        connexion.execute(
            text("""
                ALTER TABLE prediction_historique
                ADD COLUMN IF NOT EXISTS
                stock_disponible INTEGER;
            """)
        )

        print("\nColonne stock_disponible disponible.")

        # ==================================================
        # 4. AJOUTER LA QUANTITE A COMMANDER
        # ==================================================

        connexion.execute(
            text("""
                ALTER TABLE prediction_historique
                ADD COLUMN IF NOT EXISTS
                quantite_a_commander INTEGER;
            """)
        )

        print("Colonne quantite_a_commander disponible.")

        # ==================================================
        # 5. VERIFIER LES NOUVELLES COLONNES
        # ==================================================

        resultat = connexion.execute(
            text("""
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                AND table_name = 'prediction_historique'
                AND column_name IN (
                    'stock_disponible',
                    'quantite_a_commander'
                )
                ORDER BY column_name;
            """)
        )

        colonnes = resultat.all()

        print("\nVERIFICATION DES COLONNES")
        print("-" * 60)

        for colonne in colonnes:

            print(
                colonne.column_name,
                "| Type :", colonne.data_type,
                "| Nullable :", colonne.is_nullable
            )

        # Vérifier que les deux colonnes existent
        # avec le type et la configuration attendus

        if len(colonnes) != 2:

            raise RuntimeError(
                "Les deux colonnes attendues sont introuvables."
            )

        for colonne in colonnes:

            if (
                colonne.data_type != "integer"
                or colonne.is_nullable != "YES"
            ):

                raise RuntimeError(
                    f"Configuration incorrecte : "
                    f"{colonne.column_name}"
                )

        # ==================================================
        # 6. VERIFIER LA CONSERVATION DES PREDICTIONS
        # ==================================================

        nombre_apres = connexion.execute(
            text("""
                SELECT COUNT(*)
                FROM prediction_historique;
            """)
        ).scalar()

        print("\nVERIFICATION DES DONNEES")
        print("-" * 60)

        print("Nombre de prédictions avant :", nombre_avant)
        print("Nombre de prédictions après :", nombre_apres)

        if nombre_avant != nombre_apres:

            raise RuntimeError(
                "Le nombre de prédictions a changé "
                "pendant la migration."
            )

        print("Nombre de prédictions conservé.")

    # La transaction est validée à la sortie du bloc with

    print("\n" + "=" * 60)
    print("MIGRATION TERMINEE AVEC SUCCES")
    print("=" * 60)


# ==================================================
# EXECUTION DU SCRIPT
# ==================================================

if __name__ == "__main__":

    migrer_table_historique()