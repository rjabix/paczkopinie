"""
Configuration settings for the application.
"""

# Email address of the administrator account
ADMIN_EMAIL = "---"  # Change this to your admin email

def is_admin(user) -> bool:
    """Check if a user is an administrator."""
    return user is not None and user.email == ADMIN_EMAIL