# backend/models/restaurant.py

import sys
import os
from decimal import Decimal

# Add project root to sys.path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import db
from utils.map import haversine_distance


class Restaurant:
    def __init__(self, RestaurantID=None, Name=None, Description=None, Cuisine=None, Location=None,
                 Rating=None, Latitude=None, Longitude=None):
        self.RestaurantID = RestaurantID
        self.Name = Name
        self.Description= Description
        self.Cuisine = Cuisine
        self.Location = Location
        self.Rating = Rating
        self.Latitude = Latitude
        self.Longitude = Longitude

    # ----------------------------------------------------
    # Add a new restaurant
    # ----------------------------------------------------
    def add_restaurant(self):
        try:
            cursor = db.cursor(buffered=True)
            sql = """
                INSERT INTO restaurant (Name, AddressID)
                VALUES (%s, %s)
            """
            val = (self.Name, self.Location)  # Location = AddressID
            cursor.execute(sql, val)
            db.commit()
            cursor.close()
            print(f"Restaurant '{self.Name}' added successfully!")
        except Exception as e:
            print("Error adding restaurant:", e)

    # ----------------------------------------------------
    # Get all restaurants (with cuisines & avg rating)
    # ----------------------------------------------------
    @staticmethod
    def get_all_restaurants():
        try:
            cursor = db.cursor(buffered=True)
            sql = """
                SELECT 
                    r.RestaurantID,
                    r.Name,
                    GROUP_CONCAT(DISTINCT c.CuisineType SEPARATOR ', ') AS Cuisine,
                    a.Area AS Location,
                    ROUND(AVG(rt.RatingScore), 1) AS Rating,
                    Count(rt.RatingScore) As RatedBy,
                    a.Latitude,
                    a.Longitude
                FROM restaurant r
                LEFT JOIN address a ON r.AddressID = a.AddressID
                LEFT JOIN restaurantcuisine rc ON r.RestaurantID = rc.RestaurantID
                LEFT JOIN cuisine c ON rc.CuisineID = c.CuisineID
                LEFT JOIN rating rt ON r.RestaurantID = rt.RestaurantID
                GROUP BY r.RestaurantID, r.Name, a.Area, a.Latitude, a.Longitude
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()

            restaurants = []
            for r in rows:
                rid, name, cuisine, loc, rating, RatedBy, lat, lon = r
                restaurants.append({
                    "RestaurantID": rid,
                    "Name": name,
                    "Cuisine": cuisine or "N/A",
                    "Location": loc or "N/A",
                    "Rating": float(rating) if rating is not None else None,
                    "RatedBy": RatedBy if RatedBy is not None else None,
                    "Latitude": float(lat) if lat else None,
                    "Longitude": float(lon) if lon else None
                })
            return restaurants

        except Exception as e:
            print("Error fetching restaurants:", e)
            return []

    # ----------------------------------------------------
    # Get restaurants with distance from user
    # ----------------------------------------------------
    @staticmethod
    def get_all_with_distance(user_lat, user_lon):
        try:
            cursor = db.cursor(buffered=True)
            sql = """
                SELECT 
                    r.RestaurantID,
                    r.Name,
                    a.Area AS Location,
                    a.Latitude,
                    a.Longitude,
                    GROUP_CONCAT(DISTINCT c.CuisineType SEPARATOR ', ') AS Cuisine,
                    ROUND(AVG(rt.RatingScore), 1) AS Rating,
                    Count(rt.RatingScore) As RatedBy
                FROM restaurant r
                LEFT JOIN address a ON r.AddressID = a.AddressID
                LEFT JOIN restaurantcuisine rc ON r.RestaurantID = rc.RestaurantID
                LEFT JOIN cuisine c ON rc.CuisineID = c.CuisineID
                LEFT JOIN rating rt ON r.RestaurantID = rt.RestaurantID
                GROUP BY r.RestaurantID, r.Name, a.Area, a.Latitude, a.Longitude
            """
            cursor.execute(sql)
            rows = cursor.fetchall()
            cursor.close()

            restaurants = []
            for r in rows:
                rid, name, loc, lat, lon, cuisine, rating, RatedBy = r
                dist = None
                if lat and lon:
                    dist = haversine_distance(float(user_lat), float(user_lon), float(lat), float(lon))
                restaurants.append({
                    "RestaurantID": rid,
                    "Name": name,
                    "Cuisine": cuisine or "N/A",
                    "Location": loc or "N/A",
                    "Rating": float(rating) if rating is not None else None,
                    "RatedBy": RatedBy if RatedBy is not None else None,
                    "Latitude": float(lat) if lat else None,
                    "Longitude": float(lon) if lon else None,
                    "Distance_km": round(dist, 2) if dist else None
                })
            return restaurants

        except Exception as e:
            print("Error fetching restaurants with distance:", e)
            return []


# ----------------------------------------------------
# TEST (only runs if executed directly)
# ----------------------------------------------------
if __name__ == "__main__":  
    print("Fetching all restaurants...")
    all_restaurants = Restaurant.get_all_restaurants()
    print(all_restaurants)

    user_lat, user_lon = 24.8607, 67.0011
    restaurants_with_distance = Restaurant.get_all_with_distance(user_lat, user_lon)
    print("Restaurants with distance from user:")
    for r in restaurants_with_distance:
        print(r)
