
from app.db.session import SessionLocal
from app.models.commerce import Commerce, Commercant

db = SessionLocal()

try:
    # Récupérer les commerçants existants
    commercants = db.query(Commercant).all()

    if not commercants:
        print("Aucun commerçant trouvé dans la base.")

    else:
        print("Commerçants disponibles :")
        for i, commercant in enumerate(commercants, 1):
            print(f"{i}. {commercant.nom_complet}")

        choix = int(input("Numéro du commerçant : "))

        if choix < 1 or choix > len(commercants):
            raise ValueError("Numéro invalide")

        commercant = commercants[choix - 1]

        # Vérifier si le commerce existe déjà
        commerce = db.query(Commerce).filter_by(
            id_commercant=commercant.id_commercant,
            nom_commercial="Supermarché Al Amal"
        ).first()

        if commerce is None:
            commerce = Commerce(
                id_commercant=commercant.id_commercant,
                nom_commercial="Supermarché Al Amal",
                type_commerce="Supermarché",
                adresse="Adresse de démonstration",
                ville="Casablanca"
            )

            db.add(commerce)
            db.commit()
            db.refresh(commerce)

            print("Commerce créé avec succès !")
        else:
            print("Ce commerce existe déjà.")

        print("ID Commerce :", commerce.id_commerce)

except Exception as e:
    db.rollback()
    print("Erreur :", e)

finally:
    db.close()
