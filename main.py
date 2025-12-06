from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False) # Debug only for testing purposes, it allows for Python code in browser
