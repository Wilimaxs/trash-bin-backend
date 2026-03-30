import sys
import os

# Ensure we can run this script from anywhere and it finds the 'app' module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.trash_category import TrashCategory
from app.models.trash_bin import TrashBin

def seed_data():
    db = SessionLocal()
    
    try:
        print("Starting database seeding...")

        # 1. Seed Trash Bin
        existing_bin = db.query(TrashBin).filter(TrashBin.qr_code == "ECO-RVM-001").first()
        if not existing_bin:
            new_bin = TrashBin(
                qr_code="ECO-RVM-001",
                location_name="EcoBin-RVM-Alpha",
                capacity_organic=100,
                capacity_inorganic=100,
                capacity_b3=50
            )
            db.add(new_bin)
            print("- Added dummy TrashBin: EcoBin-RVM-Alpha")
        else:
            print("- TrashBin 'EcoBin-RVM-Alpha' already exists")

        # 2. Seed Trash Categories (Reward Points set to 1)
        categories = [
            # Organic
            {"compartment_type": "organic", "sub_category": "apple_waste", "reward_points": 1},
            {"compartment_type": "organic", "sub_category": "banana_peel", "reward_points": 1},
            {"compartment_type": "organic", "sub_category": "orange_peel", "reward_points": 1},
            {"compartment_type": "organic", "sub_category": "dry_leaf", "reward_points": 1},
            
            # Inorganic (Anorganik)
            {"compartment_type": "inorganic", "sub_category": "paper", "reward_points": 1},
            {"compartment_type": "inorganic", "sub_category": "bottle", "reward_points": 1},
            {"compartment_type": "inorganic", "sub_category": "paper_cup", "reward_points": 1},
            {"compartment_type": "inorganic", "sub_category": "plastic_bag", "reward_points": 1},
            {"compartment_type": "inorganic", "sub_category": "styrofoam", "reward_points": 1},
            
            # B3
            {"compartment_type": "b3", "sub_category": "battery", "reward_points": 1},
        ]

        for cat_data in categories:
            existing_cat = db.query(TrashCategory).filter(
                TrashCategory.compartment_type == cat_data["compartment_type"],
                TrashCategory.sub_category == cat_data["sub_category"]
            ).first()
            
            if not existing_cat:
                new_cat = TrashCategory(
                    compartment_type=cat_data["compartment_type"],
                    sub_category=cat_data["sub_category"],
                    reward_points=cat_data["reward_points"]
                )
                db.add(new_cat)
                print(f"- Added Category: {cat_data['compartment_type']} -> {cat_data['sub_category']}")
            else:
                print(f"- Category already exists: {cat_data['compartment_type']} -> {cat_data['sub_category']}")

        # Commit all changes to database
        db.commit()
        print("Database seeding completed successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        db.rollback()
    
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()

