import os
import requests
from models import User, Book

from flask import Flask, session, redirect, render_template, jsonify, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

GOODREADS_API_KEY="ZupLTENpaYDXX7Fz8dkCQ"
# Read API key from env variable
# GOODREADS_API_KEY = os.getenv("GOODREADS_API_KEY")

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
#create a Session
# session = db()
@app.route("/")
def index():
    isLogin = session.get('user_id') == True
    if not isLogin:
        return render_template("index.html", isLogin=isLogin)
    return render_template("search.html", isLogin=isLogin)
    # res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ZupLTENpaYDXX7Fz8dkCQ", "isbns": "9781632168146"})
    # # key: ZupLTENpaYDXX7Fz8dkCQ
    # # secret: 3Ip5oZwlIxFpagf4WhJF4QHXTOdifoVfF3P4ZFez3I
    # print(res.json())
    # return res.json()

@app.route("/register", methods=["GET","POST"])
def register():
    # Forget any user_id
    session.clear()
    if request.method == 'POST':
        """Register a new user."""
        # Ensure username
        if not request.form.get("username"):
            return render_template("error.html", message="Username not provided")
        # Ensure password
        elif not request.form.get("password"):
            return render_template("error.html", message="Password not provided")

        username = request.form.get("username")
        password = request.form.get("password")

        # Check if user exist.
        # user = db.query(User).filter_by(username=username).first()
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        user = rows.fetchone()

        if user:
            return render_template("error.html", message="Username already exists.")
        # Insert register into DB
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",{"username":username, "password":password})
        # u = User(username=username, password=password)
        # session.add(u)
        # session.commit()
        db.commit()
        return render_template("success.html", message="You have successfully registered.")
    else:
        """Show register page."""
        return render_template("register.html", type="Register")


@app.route("/login", methods=["GET","POST"])
def login():
    if session.get('user_id') == True:
        return redirect("/")

    if request.method == 'POST':
        """Login a user."""
        # Ensure username
        if not request.form.get("username"):
            return render_template("error.html", message="Username not provided")
        # Ensure password
        elif not request.form.get("password"):
            return render_template("error.html", message="Password not provided")
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if user exist.
        # user = db.query(User).filter_by(username=username).first()
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username})
        user = rows.fetchone()

        if not user:
            return render_template("error.html", message="Username does not exists.")
        if not user.password == password:
            return render_template("error.html", message="Wrong password")
        session["user_id"]=user.id
        return render_template("success.html", message="You have successfully login.")
    else:
        """Show login page."""
        return render_template("register.html", type="Login")     

@app.route("/logout", methods=["GET"])
def logout():
    """ Log user out """
    # Forget any user_id
    session.clear()
    return render_template("success.html", message="You have successfully logout.")

@app.route("/search", methods=["GET", "POST"])
def search():
    """ search a book """
    if request.method == 'POST':
        """Login a user."""
        # Ensure query is entered
        if not request.form.get("q"):
            return render_template("error.html", message="query not provided")
        # Take input and add a wildcard
        q = "%" + request.form.get("q") + "%"
        # Check if user exist.
        # user = db.query(User).filter_by(username=username).first()
        rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn LIKE :q OR \
                        title LIKE :q OR \
                        author LIKE :q LIMIT 50",
                        {"q": q})
        # Books not founded
        if rows.rowcount == 0:
            return render_template("error.html", message="We don't find books with that description.")
        
        # Fetch all the results
        books = rows.fetchall()
        isLogin = session.get('user_id') == True
        return render_template("search.html", isLogin=isLogin, books=books)
    else:
        """Show search page."""
        isLogin = session.get('user_id') == True
        if not isLogin:
            return render_template("search.html", isLogin=isLogin)
        return redirect("/")

@app.route("/books/<string:isbn>", methods=["GET", "POST"])
def books(isbn):
    # isLogin = session.get('user_id') == True
    """ save book review """
    if request.method == 'POST':
        return redirect("/books/"+isbn)
    else:
        """Show book page."""
        rows = db.execute("SELECT * FROM books WHERE isbn = :isbn LIMIT 1",{"isbn": isbn})
        book = rows.fetchone()
        # Get all reviews.
        results = db.execute("SELECT * FROM reviews \
                            INNER JOIN users \
                                ON users.id = reviews.user_id \
                            WHERE book_id = :book_id \
                            ORDER BY created_at",
                            {"book_id": book.id})
        reviews = results.fetchall()

        """ GOODREADS rating """
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_API_KEY, "isbns": book.isbn})
        # Convert to JSON
        good_books = res.json()
        # only select relevant info
        good_books = good_books['books'][0]

        return render_template("books.html", book=book, reviews=reviews)

@app.route("/api/<int:isbn>")
def book_api(isbn):
    """Return details about a single flight."""
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ZupLTENpaYDXX7Fz8dkCQ", "isbns": isbn})
    # Make sure flight exists.
    good_books = res.json()
    if books is None:
        return jsonify({"error": "Invalid isbn"}), 422
    # only select relevant info
    good_books = good_books.books[0]    # Get all reviews.
    reviews = good_books.reviews
    review_count = reviews.length
    score = 0
    for review in reviews:
        score += (review.rating)
    average_rating = score/review_count
    return jsonify({
            "title": good_books.title,
            "author": good_books.destination,
            "year": good_books.duration,
            "isbn": isbn,
            "review_count": review_count,
            "average_score": average_rating
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')