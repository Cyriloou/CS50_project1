import csv
import os

from flask import Flask, render_template, request
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    f = open("books.csv")
    csvreader = csv.reader(f)
    # This skips the first row of the CSV file.
    # csvreader.next() also works in Python 2.
    next(csvreader)
    for isbn, title, author, year in csvreader:
        book = Book(isbn=isbn,title=title,author=author,year=int(year))
        db.session.add(book)
        print(f"Added book from {isbn} title {title} from {author} published in {year}.")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()
