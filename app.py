from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
import requests
from constants import (
    GOOGLE_BOOKS_API_KEY,
    GOOGLE_BOOKS_API_MAX_RESULTS,
    GOOGLE_BOOKS_API_URL,
)

app = Flask(__name__)

# Initialize Firestore DB
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
books_ref = db.collection("books")


@app.route("/api/books", methods=["POST"])
def addBookToInventory():
    try:
        books_ref.add(request.json)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error Occured: {e}"


@app.route("/api/books", methods=["GET"])
def getBooksFromInventory():
    try:
        all_books = [book.to_dict() for book in books_ref.stream()]
        return jsonify(all_books), 200
    except Exception as e:
        return f"An Error Occured: {e}"


@app.route("/api/books/<book_id>", methods=["PUT"])
def updateBookInInventory(book_id):
    try:
        books_ref.document(book_id).set(request.json)
        return jsonify("put world"), 200
    except Exception as e:
        return f"An Error Occured: {e}"


@app.route("/api/books/search", methods=["GET"])
def searchBook():
    book_name = request.args.get("query")
    payload = {
        "key": GOOGLE_BOOKS_API_KEY,
        "maxResults": GOOGLE_BOOKS_API_MAX_RESULTS,
        "q": book_name,
    }
    resp = requests.get(GOOGLE_BOOKS_API_URL, params=payload)
    if resp.status_code != 200:
        raise Exception(f"GET /search/ {resp.status_code}")
    return jsonify(resp.json()), 200


if __name__ == "__main__":
    app.run()