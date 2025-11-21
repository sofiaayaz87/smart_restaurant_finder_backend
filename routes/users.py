import sys
import os
import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.useraccount import UserAccount
from utils.email import send_otp_email

users_bp = Blueprint("users", __name__)
otp_storage = {}  # In-memory OTP store

# ------------------------- LOGIN / SIGNUP -------------------------
@users_bp.route("/login", methods=["POST"])
def login_user():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email:
        return jsonify({"error": "email is required"}), 400

    user_row = UserAccount.get_by_email(email)
    if user_row:
        if not password:
            return jsonify({"error": "password required for existing user"}), 400
        ok, user = UserAccount.verify_login(email, password)
        if ok:
            return jsonify({"message": "login successful", "user": UserAccount.row_to_dict(user)}), 200
        else:
            return jsonify({"error": "invalid credentials"}), 401

    else:
        return jsonify({"error": "invalid credentials"}), 401

@users_bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email:
        return jsonify({"error": "email is required"}), 400
    
    if not password:
        return jsonify({"error": "password is required"}), 400

    user_row = UserAccount.get_by_email(email)
    if user_row:
        return jsonify({"error": "Email Already Exist"}), 401

    # 1️⃣ CREATE USER IN DATABASE (UNVERIFIED)
    user = UserAccount(
        FirstName=data.get("first_name"),
        LastName=data.get("last_name"),
        Email=email,
        ContactNo=data.get("contact"),
        Password=password,
        Role="user"
    )

    success, created_user = user.register_user()
    if not success:
        return jsonify({"error": "Failed to save user"}), 500

    # 2️⃣ GENERATE OTP
    otp = random.randint(100000, 999999)
    expires = datetime.utcnow() + timedelta(minutes=5)

    otp_storage[email] = {
        "otp": otp,
        "expires": expires
    }

    # 3️⃣ SEND OTP EMAIL
    try:
        send_otp_email(email, otp)
    except Exception as e:
        print("Email error:", e)

    return jsonify({
        "message": "User created. OTP sent",
        "user": UserAccount.row_to_dict(created_user),
        "otp": otp
    }), 201


# ------------------------- VERIFY OTP -------------------------
@users_bp.route("/verify_otp", methods=["POST"])
def verify_otp():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    otp_input = data.get("otp")

    if not email or not otp_input:
        return jsonify({"error": "email and otp required"}), 400

    record = otp_storage.get(email)
    if not record:
        return jsonify({"error": "no OTP requested for this email"}), 400

    if datetime.utcnow() > record["expires"]:
        otp_storage.pop(email, None)
        return jsonify({"error": "otp expired"}), 400

    if int(otp_input) != record["otp"]:
        return jsonify({"error": "invalid otp"}), 400

    # 1️⃣ MARK EMAIL VERIFIED IN DB
    cursor = db.cursor()
    cursor.execute("UPDATE useraccount SET IsEmailVerified = 1 WHERE Email = %s", (email,))
    db.commit()
    cursor.close()

    otp_storage.pop(email, None)

    return jsonify({"message": "OTP verified successfully"}), 200

# ------------------------- FAVORITES -------------------------
@users_bp.route("/users/<int:user_id>/favorites", methods=["POST"])
def add_favorite(user_id):
    data = request.get_json(force=True)
    restaurant_id = data.get("restaurant_id")
    if not restaurant_id:
        return jsonify({"error": "restaurant_id required"}), 400
    ok = UserAccount.add_favorite(user_id, restaurant_id)
    if ok:
        return jsonify({"message": "added to favorites"}), 200
    return jsonify({"error": "failed to add favorite"}), 500

@users_bp.route("/users/<int:user_id>/favorites/<int:restaurant_id>", methods=["DELETE"])
def remove_favorite(user_id, restaurant_id):
    ok = UserAccount.remove_favorite(user_id, restaurant_id)
    if ok:
        return jsonify({"message": "removed from favorites"}), 200
    return jsonify({"error": "failed to remove favorite"}), 500

@users_bp.route("/users/<int:user_id>/favorites", methods=["GET"])
def get_favorites(user_id):
    rows = UserAccount.get_favorites(user_id)
    return jsonify(rows), 200

# ------------------------- PROFILE UPDATE -------------------------
@users_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    data = request.get_json(force=True)
    ok = UserAccount.update_profile(user_id, **data)
    if ok:
        return jsonify({"message": "profile updated"}), 200
    return jsonify({"error": "failed to update profile"}), 500
