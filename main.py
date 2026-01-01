from website import create_app
import os.path
from dotenv import load_dotenv

# Load .env file only if it exists, for local development
if os.path.exists('.env'):
    load_dotenv()

app = create_app()

if __name__ == '__main__':
    env = os.environ.get("ENVIRONMENT")
    print(" * Environment: " + env)
    if env == "local":
        app.run(debug=True) # Debug only for testing purposes, it allows for Python code in browser
    else:
        app.run(debug=False)
