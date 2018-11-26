import _mysql
from flask import Flask, request, jsonify, redirect, url_for, render_template, send_from_directory,session, abort,json,flash
import os
import prettyprint
import sys

PATH = os.path.dirname(os.path.abspath(__file__))
app=Flask("cop4710_flask_asg5", template_folder=os.path.join(PATH, 'templates'), static_folder=os.path.join(PATH, 'static'))

db = _mysql.connect(host="localhost",
                    user='flask_user',
                    passwd='cop4710',
                    db="book")


def get_book_data(title):
    db.query("SELECT title, authorFirst, authorLast, branchName, price, quality FROM book.book INNER JOIN copy, wrote, author, branch WHERE book.title LIKE '%"+title.decode("utf8")+"%' AND book.bookCode = copy.bookCode AND book.bookCode = wrote.bookCode AND wrote.authorNum = author.authorNum And copy.branchNum = branch.branchNum;")
    r = db.store_result().fetch_row(0)
    book = {}
    i = 0
    for x in r:
        book[i] = {"title": x[0].decode('utf8'),
                    "authorFirst": x[1].decode('utf8'),
                    "authorLast": x[2].decode('utf8'),
                    "branchName": x[3].decode('utf8'),
                    "price": x[4],
                    "quality": x[5].decode('utf8')
                    }
        i = i + 1
    return book

@app.route("/")
def index():
    return render_template("content.html", page="home")

@app.route("/books")
def books():
    db.query("select * from book.book")
    r = db.store_result().fetch_row(0)
    books = {}
    for x in r:
        books[x[0].decode('utf8')] = {"title": x[1].decode('utf8'), "publisherCode": x[2].decode('utf8'),
                                      "type": x[3].decode('utf8'), "paperback": x[4].decode('utf8')}
    return render_template("content.html", page="books", data = books)

@app.route("/books/search", methods=["POST"])
def book_search():
    return render_template("book_info.html", book=get_book_data(request.get_data()))

@app.route("/books/delete", methods=["POST"])
def book_delete():
    data = request.get_data().decode("utf8")
    db.query("DELETE FROM book where bookCode = '" + data + "';")
    return "/books"

@app.route("/books/add", methods=["POST"])
def book_add():
    bookCode = request.form['bookCode']
    title = request.form['title']
    publisherCode = request.form['publisherCode']
    type = request.form['type']
    paperback = request.form['paperback']
    db.query("INSERT INTO book(bookCode, title, publisherCode, type, paperback) VALUES(" + bookCode + ", '" + title + "','" + publisherCode+ "', '" + type + "', '" + paperback + "');")
    return redirect("/books")

@app.route("/copies")
def copies():
    db.query("SELECT title, branchName, copyNum, quality, price, copy.bookCode, copy.branchNum FROM book.copy INNER JOIN book, branch WHERE copy.bookCode = book.bookCode AND copy.branchNum = branch.branchNum;")
    r = db.store_result().fetch_row(0)
    copies = {}
    i = 0
    for x in r:
        copies[i] = {"title": x[0].decode('utf8'), "branchName": x[1].decode('utf8'), "copyNum": x[2],
                    "quality": x[3].decode('utf8'), "price": x[4], "bookCode": x[5].decode("utf8"), "branchNum": x[6]}
        i = i + 1
    return render_template("content.html", page="copies", data=copies)

@app.route("/copies/delete", methods=["POST"])
def copy_delete():
    bookCode = request.form['bookCode']
    branchNum = request.form['branchNum']
    copyNum = request.form['copyNum']
    db.query("DELETE FROM copy WHERE bookCode = '" + bookCode + "' AND branchNum = '" + branchNum + "' AND copyNum = '" + copyNum + "';")
    return "/copies"

@app.route("/copies/add", methods=["POST"])
def copy_add():
    bookCode = request.form['bookCode']
    branchNum = request.form['branchNum']
    copyNum = request.form['copyNum']
    quality = request.form['quality']
    price = request.form['price']
    db.query("INSERT INTO copy(bookCode, branchNum, copyNum, quality, price) VALUES (" + bookCode + ", " + branchNum + ", " +  copyNum + ", '" + quality + "', " + price + ");")
    return redirect("/copies")

@app.route("/publishers")
def publishers():
    db.query("SELECT * FROM publisher;")
    r = db.store_result().fetch_row(0)
    publishers = {}
    for x in r:
        publishers[x[0].decode('utf8')] = {"publisherName": x[1].decode('utf8'), "city": x[2].decode('utf8')}

    return render_template("content.html", page="publishers", data=publishers)

@app.route("/publishers/add", methods=["POST"])
def publisher_add():
    publisherCode = request.form['publisherCode']
    publisherName = request.form['publisherName']
    city = request.form['city']
    db.query("INSERT INTO publisher(publisherCode, publisherName, city) VALUES ('" + publisherCode + "', '" + publisherName + "', '" +  city + "');")
    return redirect("/publishers")

@app.route("/publishers/delete", methods=["POST"])
def publisher_delete():
    data = request.get_data().decode("utf8")
    db.query("DELETE FROM publisher WHERE publisherCode = '" + data + "';")
    return "/publishers"

@app.route("/publishers/edit", methods=["POST"])
def publisher_edit():
    publisherCode = request.form['publisherCode']
    publisherName = request.form['publisherName']
    city = request.form['city']
    db.query("UPDATE publisher SET publisherName = '" + publisherName + "', city = '" + city + "' WHERE publisherCode = '" + publisherCode + "';")
    return redirect('/publishers')

@app.route("/authors")
def authors():
    db.query("SELECT * FROM author;")
    r = db.store_result().fetch_row(0)
    authors = {}
    for x in r:
        authors[x[0]] = {"authorLast": x[1].decode('utf8'), "authorFirst": x[2].decode('utf8')}
    return render_template("content.html", page="authors", data=authors)

@app.route("/authors/add", methods=["POST"])
def author_add():
    authorFirst = request.form['authorFirst']
    authorLast = request.form['authorLast']
    db.query("SELECT COUNT(authorNum) FROM book.author;")
    authorNum = int(db.store_result().fetch_row(0)[0][0]) + 1
    db.query("INSERT INTO author(authorLast, authorFirst, authorNum) VALUES ('" + authorLast + "', '" + authorFirst + "', " + str(authorNum) + ");")
    return redirect("/authors")

@app.route("/authors/delete", methods=["POST"])
def author_delete():
    data = request.get_data().decode("utf8")
    db.query("DELETE FROM author where authorNum = " + data + ";")
    return "/authors"

@app.route("/authors/edit", methods=["POST"])
def author_edit():
    authorFirst = request.form['authorFirst']
    authorLast = request.form['authorLast']
    authorNum = request.form['authorNum']
    db.query("UPDATE author SET authorFirst = '" + authorFirst + "', authorLast = '" + authorLast + "' WHERE authorNum = " + authorNum + ";");
    return redirect("/authors")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)