# backend/routes/restaurants.py

import sys
import os
from flask import Blueprint, jsonify, request
import urllib.parse

# -------------------------
# Add project root to sys.path
# -------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.restaurant import Restaurant

# -------------------------
# Blueprint
# -------------------------
restaurants_bp = Blueprint('restaurants', __name__)

# -------------------------
# Recommend restaurants route
# -------------------------
@restaurants_bp.route("/recommend", methods=["GET"])
def recommend_restaurants():
    """
    Endpoint: /recommend?user_lat=24.86&user_lon=67.0
    - user_lat, user_lon: optional user location to sort by distance
    """
    # Get query params
    user_lat = request.args.get("user_lat", type=float)
    user_lon = request.args.get("user_lon", type=float)

    # Fetch all restaurants
    if user_lat is not None and user_lon is not None:
        all_restaurants = Restaurant.get_all_with_distance(user_lat, user_lon)
    else:
        all_restaurants = Restaurant.get_all_restaurants()
        # Add None distance for consistency
        for r in all_restaurants:
            r["Distance_km"] = None

    # Sort: first by distance if available, else by rating descending
    def sort_key(r):
        if r["Distance_km"] is not None:
            return (r["Distance_km"], -r["Rating"] if r["Rating"] else 0)
        else:
            return -(r["Rating"] if r["Rating"] else 0)

    sorted_restaurants = sorted(all_restaurants, key=sort_key)

    # Add Google Maps URL
    for r in sorted_restaurants:
        lat = r.get("Latitude")
        lon = r.get("Longitude")
        loc = r.get("Location")

        if lat and lon:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        else:
            encoded_address = urllib.parse.quote_plus(str(loc))
            maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"

        r["MapsURL"] = maps_url

    return jsonify(sorted_restaurants)
