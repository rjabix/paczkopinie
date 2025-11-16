"""
Configuration settings for the application.
"""
import os

def get_admin_email() -> str:
    """Get the administrator email from environment or config."""
    env: str = None
    try:
        if os.environ.get("ENVIRONMENT") == "DEV":
            env = "DEV"
    finally:
        env = "Local" if env is None else "DEV"

    if env == "DEV":
        return os.environ.get("ADMIN_EMAIL")
    return "282163@student.pwr.edu.pl"

# Email address of the administrator account
ADMIN_EMAIL = get_admin_email()

def is_admin(user) -> bool:
    """Check if a user is an administrator."""
    return user is not None and user.email == ADMIN_EMAIL
