from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_admin import credentials, firestore, initialize_app
import requests
from http import HTTPStatus
from book import Book
from constants import (
    GOOGLE_BOOKS_API_KEY,
    GOOGLE_BOOKS_API_MAX_RESULTS,
    GOOGLE_BOOKS_API_URL,
)

app = Flask(__name__)
CORS(app)

# Initialize Firestore DB
cred = credentials.Certificate("key.json")
default_app = initialize_app(cred)
db = firestore.client()
books_ref = db.collection("books")


@app.route("/api/books", methods=["POST"])
def addBookToInventory():
    try:
        book = Book(
            id=request.json["id"],
            title=request.json["title"],
            thumbnail=request.json["thumbnail"],
            quantity=1,
            link=request.json["link"],
        )
        books_ref.document(request.json["id"]).set(book.to_dict())
        return jsonify(request.json), HTTPStatus.CREATED
    except Exception as e:
        return jsonify(f"An Error Occured: {e}"), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/api/books", methods=["GET"])
def getBooksFromInventory():
    try:
        all_books = [book.to_dict() for book in books_ref.stream()]
        return jsonify(all_books), HTTPStatus.OK
    except Exception as e:
        return jsonify(f"An Error Occured: {e}"), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/api/books/<book_id>/<action>", methods=["PUT"])
def updateBookInInventory(book_id, action):
    try:
        book = books_ref.document(book_id).get()
        if book.exists:
            book = book.to_dict()
            if action == "add":
                book["quantity"] = book["quantity"] + 1
            else:
                if book["quantity"] > 0:
                    book["quantity"] = book["quantity"] - 1
            books_ref.document(book_id).set(book)
            return jsonify(book), HTTPStatus.OK
        else:
            return jsonify({}), HTTPStatus.NOT_FOUND
    except Exception as e:
        return jsonify(f"An Error Occured: {e}"), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/api/books/<book_id>", methods=["DELETE"])
def deleteBookInInventory(book_id):
    try:
        books_ref.document(book_id).delete()
        return jsonify({}), HTTPStatus.NO_CONTENT
    except Exception as e:
        return jsonify(f"An Error Occured: {e}"), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/api/books/search", methods=["GET"])
def searchBook():
    try:
        search_query = request.args.get("query")

        payload = {
            "key": GOOGLE_BOOKS_API_KEY,
            "maxResults": GOOGLE_BOOKS_API_MAX_RESULTS,
            "q": search_query,
        }

        resp = requests.get(GOOGLE_BOOKS_API_URL, params=payload)
        if resp.status_code != 200:
            return jsonify("Upstream API failed"), HTTPStatus.BAD_GATEWAY

        search_results = resp.json().get("items")
        search_results = normalize_upstream_response(search_results)

        return jsonify(search_results), HTTPStatus.OK
    except Exception as e:
        return jsonify(f"An Error Occured: {e}"), HTTPStatus.INTERNAL_SERVER_ERROR


def normalize_upstream_response(results):
    mapped_results = []
    for book_meta in results:
        book = books_ref.document(book_meta["id"]).get()

        bookObj = {
            "id": book_meta["id"],
            "title": book_meta["volumeInfo"]["title"],
            "thumbnail": book_meta["volumeInfo"]["imageLinks"]["smallThumbnail"],
            "link": book_meta["volumeInfo"]["infoLink"],
            "is_available_in_inventory": book.exists,
        }

        mapped_results.append(bookObj)
    return mapped_results


if __name__ == "__main__":
    app.run()