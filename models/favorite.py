# backend/models/favorite.py

import sys
import os
from config import db

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Favorite:
    @staticmethod
    def add(user_id, restaurant_id):
        cursor = db.cursor(buffered=True)
        try:
            # check if already exists
            cursor.execute("SELECT * FROM favorite WHERE UserID=%s AND RestaurantID=%s", (user_id, restaurant_id))
            if cursor.fetchone():
                cursor.close()
                return False, "Already in favorites"

            cursor.execute(
                "INSERT INTO favorite (UserID, RestaurantID) VALUES (%s,%s)",
                (user_id, restaurant_id)
            )
            db.commit()
            cursor.close()
            return True, "Added to favorites"
        except Exception as e:
            cursor.close()
            return False, str(e)

    @staticmethod
    def remove(user_id, restaurant_id):
        cursor = db.cursor(buffered=True)
        try:
            cursor.execute("DELETE FROM favorite WHERE UserID=%s AND RestaurantID=%s", (user_id, restaurant_id))
            db.commit()
            cursor.close()
            return True, "Removed from favorites"
        except Exception as e:
            cursor.close()
            return False, str(e)

    @staticmethod
    def list(user_id):
        cursor = db.cursor(buffered=True)
        try:
            cursor.execute("""
                SELECT r.RestaurantID, r.Name, r.PriceRange, r.AvgRating
                FROM restaurant r
                INNER JOIN favorite f ON r.RestaurantID=f.RestaurantID
                WHERE f.UserID=%s
            """, (user_id,))
            rows = cursor.fetchall()
            cursor.close()
            keys = ["RestaurantID", "Name", "PriceRange", "AvgRating"]
            return [dict(zip(keys, r)) for r in rows]
        except Exception as e:
            cursor.close()
            return []
