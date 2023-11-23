from app import app
if __name__ == "__main__":
    print("Running the web app")
    app.run(host="127.0.0.1", port=5000, debug=True)
    from app import db

