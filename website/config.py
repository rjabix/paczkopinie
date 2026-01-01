# Globally accessible variables, functions for HTML templates
import os

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

def is_admin(user) -> bool:
    return user is not None and user.email == ADMIN_EMAIL
