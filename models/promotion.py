# backend/models/promotion.py

import sys
import os
from datetime import datetime
from config import db

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Promotion:
    def __init__(self, PromotionID=None, RestaurantID=None, Title=None, Description=None, Discount=None,
                 ValidFrom=None, ValidTo=None, IsActive=1, CreatedAt=None):
        self.PromotionID = PromotionID
        self.RestaurantID = RestaurantID
        self.Title = Title
        self.Description = Description
        self.Discount = Discount
        self.ValidFrom = ValidFrom
        self.ValidTo = ValidTo
        self.IsActive = IsActive
        self.CreatedAt = CreatedAt or datetime.now()

    # List promotions for restaurant
    @staticmethod
    def get_for_restaurant(restaurant_id):
        cursor = db.cursor(buffered=True)
        sql = """SELECT PromotionID, RestaurantID, Title, Description, Discount,
                 ValidFrom, ValidTo, IsActive, CreatedAt
                 FROM promotion WHERE RestaurantID=%s AND IsActive=1"""
        cursor.execute(sql, (restaurant_id,))
        rows = cursor.fetchall()
        cursor.close()
        keys = ["PromotionID","RestaurantID","Title","Description","Discount","ValidFrom","ValidTo","IsActive","CreatedAt"]
        return [dict(zip(keys, r)) for r in rows]

    # Create promotion
    def create(self):
        cursor = db.cursor(buffered=True)
        sql = """INSERT INTO promotion
                 (RestaurantID, Title, Description, Discount, ValidFrom, ValidTo, IsActive, CreatedAt)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
        try:
            cursor.execute(sql, (
                self.RestaurantID, self.Title, self.Description, self.Discount,
                self.ValidFrom, self.ValidTo, self.IsActive, self.CreatedAt
            ))
            db.commit()
            self.PromotionID = cursor.lastrowid
            cursor.close()
            return True, self.PromotionID
        except Exception as e:
            cursor.close()
            return False, str(e)

    # Update promotion
    @staticmethod
    def update(promotion_id, **kwargs):
        allowed = ["Title","Description","Discount","ValidFrom","ValidTo","IsActive"]
        set_parts = []
        params = []
        for k,v in kwargs.items():
            if k in allowed:
                set_parts.append(f"{k}=%s")
                params.append(v)
        if not set_parts:
            return False, "No valid fields to update"
        params.append(promotion_id)
        sql = f"UPDATE promotion SET {', '.join(set_parts)} WHERE PromotionID=%s"
        cursor = db.cursor(buffered=True)
        try:
            cursor.execute(sql, tuple(params))
            db.commit()
            cursor.close()
            return True, "Updated"
        except Exception as e:
            cursor.close()
            return False, str(e)

    # Soft delete
    @staticmethod
    def delete(promotion_id):
        return Promotion.update(promotion_id, IsActive=0)
