# backend/app.py

from flask import Flask
from routes.restaurants import restaurants_bp
from routes.users import users_bp
from routes.reservations import reservations_bp  
from routes.recommend import recommend_bp
from routes.menu import menu_bp
from routes.favorites import favorites_bp
from routes.photos import photos_bp
from routes.promotions import promotions_bp

app = Flask(__name__)

app.register_blueprint(restaurants_bp, url_prefix="/restaurants")
app.register_blueprint(users_bp, url_prefix="/users")
app.register_blueprint(reservations_bp, url_prefix="/reservations") 
app.register_blueprint(recommend_bp, url_prefix="/recommend")
app.register_blueprint(menu_bp, url_prefix="/menu")
app.register_blueprint(favorites_bp, url_prefix="/favorites")
app.register_blueprint(photos_bp, url_prefix="/photos")
app.register_blueprint(promotions_bp, url_prefix="/promotions")

@app.route("/")
def home():
    return "Smart Restaurant API is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
