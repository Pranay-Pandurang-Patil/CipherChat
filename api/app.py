from flask import Flask, request, jsonify
import sys
import os


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.append(PROJECT_ROOT)


# =========================================================
# IMPORT EXISTING AUTHENTICATION LOGIC
# =========================================================

from server.auth import register_user, login_user

from database.database import (
    get_all_users,
    get_private_messages
)


# =========================================================
# CREATE FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "message": "CipherChat API is running."
    })


# =========================================================
# REGISTER
# =========================================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")

    success = register_user(
        username,
        email,
        password
    )

    if success:

        return jsonify({
            "success": True,
            "message": "Registration successful."
        })

    return jsonify({
        "success": False,
        "message": "Registration failed."
    }), 400


# =========================================================
# LOGIN
# =========================================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json()

    username = data.get("username", "")
    password = data.get("password", "")

    success = login_user(
        username,
        password
    )

    if success:

        return jsonify({
            "success": True,
            "message": "Login successful.",
            "username": username
        })

    return jsonify({
        "success": False,
        "message": "Invalid username or password."
    }), 401

# =========================================================
# GET USERS
# =========================================================

@app.route("/api/users", methods=["GET"])
def get_users():

    users = get_all_users()

    user_list = []

    for username, email in users:

        user_list.append({
            "username": username,
            "email": email
        })

    return jsonify(user_list)

# =========================================================
# GET PRIVATE CHAT HISTORY
# =========================================================

@app.route("/api/private-messages", methods=["GET"])
def private_messages():

    username = request.args.get(
        "username",
        ""
    )

    other_username = request.args.get(
        "other_username",
        ""
    )


    # Both usernames are required.
    if (
        username == ""
        or
        other_username == ""
    ):

        return jsonify({
            "success": False,
            "message": "Both usernames are required."
        }), 400


    messages = get_private_messages(
        username,
        other_username
    )


    message_list = []


    for sender, message, created_at in messages:

        message_list.append({
            "sender": sender,
            "text": message,
            "time": created_at
        })


    return jsonify({
        "success": True,
        "messages": message_list
    })
# =========================================================
# START API SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )