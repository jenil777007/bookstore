from flask import Flask
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
books_ref = db.collection("books")


@app.route("/api/books")
def hello():
    return {"data": "string"}


if __name__ == "__main__":
    app.run()