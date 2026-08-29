"""In-code user store for this TP.

Only one user (admin) is allowed to access the API. Credentials are defined
directly in the source code. The password is stored as a bcrypt
hash.

Default credentials:
    username: admin
    password: admin123
"""

import bcrypt

ADMIN_USERNAME = "admin"
_ADMIN_PASSWORD_HASH = b"$2b$12$ylGU9ClpPREcdIlPVTGgPOEpkSS.lodTpguQvljdvV0gkom.Skjq6"


def authenticate_user(username: str, password: str) -> bool:
    if username != ADMIN_USERNAME:
        return False
    return bcrypt.checkpw(password.encode("utf-8"), _ADMIN_PASSWORD_HASH)
