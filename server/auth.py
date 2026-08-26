from database.database import add_user, get_user, check_password


def valid_username(username):

    # Username cannot be empty.
    if username == "":
        return False

    # Username cannot be longer than 20 characters.
    if len(username) > 20:
        return False

    # Allow only letters, numbers and underscore.
    for character in username:

        if not (character.isalnum() or character == "_"):
            return False

    return True

def valid_email(email):

    # Email must contain exactly one @ symbol.
    if email.count("@") != 1:
        return False

    # Separate the username and domain.
    username, domain = email.split("@")

    # Both parts must contain something.
    if username == "" or domain == "":
        return False

    # Domain should contain a dot.
    if "." not in domain:
        return False

    # Dot cannot be the first or last character of the domain.
    if domain.startswith(".") or domain.endswith("."):
        return False

    # The email should not contain spaces.
    if " " in email:
        return False

    return True

def register_user(username, email, password):

    # Validate the username.
    if not valid_username(username):
        return False

    # Validate the email.
    if not valid_email(email):
        return False

    # Password cannot be empty.
    if password == "":
        return False

    # Store the user in SQLite.
    return add_user(
        username,
        email,
        password
    )


def login_user(username, password):

    # Validate the username.
    if not valid_username(username):
        return False

    # Find the user.
    user = get_user(username)

    # User does not exist.
    if user is None:
        return False

    # Database structure:
    #
    # user[0] = id
    # user[1] = username
    # user[2] = email
    # user[3] = password_hash
    # user[4] = salt

    stored_hash = user[3]
    salt = user[4]

    # Verify the password.
    return check_password(
        password,
        stored_hash,
        salt
    )