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
    get_private_messages,
    save_message,
    create_room,
    join_room,
    get_room,
    get_room_members,
    get_room_messages
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
# SEND PRIVATE MESSAGE
# =========================================================

@app.route("/api/private-messages", methods=["POST"])
def send_private_message():

    data = request.get_json()


    sender = data.get(
        "sender",
        ""
    )

    receiver = data.get(
        "receiver",
        ""
    )

    message = data.get(
        "message",
        ""
    ).strip()


    # Validate required fields.
    if (
        sender == ""
        or
        receiver == ""
        or
        message == ""
    ):

        return jsonify({
            "success": False,
            "message": "Sender, receiver and message are required."
        }), 400


    # Keep the same 500-character
    # message limit as the TCP server.
    if len(message) > 500:

        return jsonify({
            "success": False,
            "message": "Message is too long."
        }), 400


    # Save private message to SQLite.
    success = save_message(
        sender,
        receiver,
        message
    )


    if not success:

        return jsonify({
            "success": False,
            "message": "Unable to send message."
        }), 400


    return jsonify({
        "success": True,
        "message": "Message sent."
    })

@app.route("/api/rooms", methods=["POST"])
def create_new_room():
    data = request.get_json()

    username = data.get("username")
    room_name = data.get("room_name")
    room_type = data.get("room_type", "group")

    if not username or not room_name:
        return jsonify({
            "success": False,
            "message": "Username and room name are required"
        }), 400

    room_code = create_room(username, room_name, room_type)

    if not room_code:
        return jsonify({
            "success": False,
            "message": "Room creation failed"
        }), 500

    return jsonify({
        "success": True,
        "room_code": room_code
    }), 201

@app.route("/api/rooms/join", methods=["POST"])
def join_existing_room():

    data = request.get_json()

    username = data.get("username", "")
    room_code = data.get("room_code", "").strip()

    if not username or not room_code:

        return jsonify({
            "success": False,
            "message": "Username and room code are required."
        }), 400

    success = join_room(
        username,
        room_code
    )

    if not success:

        return jsonify({
            "success": False,
            "message": "Unable to join room."
        }), 400

    return jsonify({
        "success": True,
        "message": "Joined room successfully."
    })

# =========================================================
# GET ROOM DETAILS
# =========================================================

@app.route("/api/rooms/<room_code>", methods=["GET"])
def room_details(room_code):

    room = get_room(room_code)

    if not room:

        return jsonify({
            "success": False,
            "message": "Room not found."
        }), 404

    members = get_room_members(room_code)

    member_list = []

    for username, role in members:

        member_list.append({
            "username": username,
            "role": role
        })

    return jsonify({
        "success": True,
        "room": {
            "code": room_code,
            "name": room[1],
            "type": room[2],
            "members": member_list
        }
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