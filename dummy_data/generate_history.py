import os
import random
import sys
from datetime import timedelta

# Allow this script to import the app package when run from the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app.core.config import get_wib_time
from app.db.session import SessionLocal
from app.models.disposal_history import DisposalHistory
from app.models.trash_bin import TrashBin
from app.models.trash_category import TrashCategory
from app.models.user import User

# Simple config: adjust only these values if needed.
TARGET_USER_ID = 1
TOTAL_ROWS = 40


def generate_dummy_history() -> None:
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.id == TARGET_USER_ID).first()
        if not user:
            print(f"[ERROR] User with id={TARGET_USER_ID} not found.")
            return

        bins = db.query(TrashBin).all()
        categories = db.query(TrashCategory).all()

        if not bins:
            print("[ERROR] No trash bin found. Please seed trash bin data first.")
            return

        if not categories:
            print("[ERROR] No trash category found. Please seed category data first.")
            return

        now = get_wib_time()

        for i in range(TOTAL_ROWS):
            category = random.choice(categories)
            selected_bin = random.choice(bins)

            # Ensure the first 5 rows are generated strictly for "today"
            if i < 5:
                # Random time within the last 12 hours of today
                random_minutes = random.randint(0, 720)
                created_at = now - timedelta(minutes=random_minutes)
            else:
                # Spread timestamps over roughly the last 60 days for better UI grouping.
                random_days_ago = random.randint(1, 59)
                random_minutes = random.randint(0, 1439)
                created_at = now - timedelta(days=random_days_ago, minutes=random_minutes)

            # noinspection PyTypeChecker
            row = DisposalHistory(
                user_id=user.id,
                trash_bin_id=selected_bin.id,
                trash_category_id=category.id,
                points_earned=category.reward_points,
                image_url=None,
                created_at=created_at,
                updated_at=created_at,
            )
            db.add(row)

            # Tambahkan poin yang didapat ke total poin user
            user.total_points += category.reward_points

        db.commit()
        print(f"[SUCCESS] Inserted {TOTAL_ROWS} dummy disposal histories for user_id={TARGET_USER_ID}.")

    except Exception as exc:
        db.rollback()
        print(f"[ERROR] Failed to generate dummy history: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    generate_dummy_history()
