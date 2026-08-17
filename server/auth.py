from database.database import add_user, get_user, check_password


def valid_username(username):

    # Username cannot be empty.
    if username == "":
        return False

    # Username cannot be longer than 20 characters.
    if len(username) > 20:
        return False

    # Check every character.
    for character in username:

        # Allow letters, numbers and underscore.
        if not (character.isalnum() or character == "_"):
            return False

    return True


def register_user(username, password):

    # Check whether the username follows our rules.
    if not valid_username(username):
        return False

    # Add the user to SQLite.
    return add_user(username, password)


def login_user(username, password):

    # Check whether the username follows our rules.
    if not valid_username(username):
        return False

    # Find the user in SQLite.
    user = get_user(username)

    # User does not exist.
    if user is None:
        return False

    # Get stored password information.
    stored_hash = user[1]
    salt = user[2]

    # Check whether the password is correct.
    return check_password(
        password,
        stored_hash,
        salt
    )