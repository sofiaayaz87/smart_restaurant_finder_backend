import sys
import os
from config import db

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Menu:
    @staticmethod
    def get_menu_by_restaurant(res_id):
        cursor = db.cursor(dictionary=True)
        sql = """
            SELECT m.MenuID, m.RestaurantID, m.MenuName,
                   mi.MenuItemID, mi.ItemName, mi.Description, 
                   mi.Price, mi.IsAvailable
            FROM menu m
            LEFT JOIN menuitem mi ON m.MenuID = mi.MenuID
            WHERE m.RestaurantID = %s
        """
        cursor.execute(sql, (res_id,))
        rows = cursor.fetchall()
        cursor.close()
        return rows

    @staticmethod
    def get_single_item(item_id):
        cursor = db.cursor(dictionary=True)
        sql = "SELECT * FROM menuitem WHERE MenuItemID = %s"
        cursor.execute(sql, (item_id,))
        row = cursor.fetchone()
        cursor.close()
        return row
