import os
import datetime
import json


from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///exams.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # add stock name, add current lookup value, add total value
    # return render_template("index.html", rows=rows, cash=usd(cash), sum=usd(sum))
    return redirect("/exams")
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # if request method is GET, display buy.html form
    if request.method == "GET":
        return render_template("buy.html")

    # if request method is POST
    else:
        # save stock symbol, number of shares, and quote dict from form
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        quote = lookup(symbol)

        # return apology if symbol not provided or invalid
        if quote == None:
            return apology("must provide valid stock symbol", 400)

        # return apology if shares not provided. buy form only accepts positive integers
        if not shares:
            return apology("must provide number of shares", 400)

        # cast symbol to uppercase and cast shares to int, in order to work with them
        symbol = symbol.upper()
        shares = int(shares)
        purchase = quote['price'] * shares

        # make sure user can afford current stock, checking amount of cash in users table

        # select this user's cash balance from users table
        balance = db.execute("SELECT cash FROM users WHERE id = :id", id=session["user_id"])
        balance = balance[0]['cash']
        remainder = balance - purchase
        # print("balance: ", balance)
        # print("remainder: ", remainder)

        # if purchase price exceeds balance, return error
        if remainder < 0:
            return apology("insufficient funds", 400)

        # query portfolio table for row with this userid and stock symbol:
        row = db.execute("SELECT * FROM portfolio WHERE userid = :id AND symbol = :symbol",
                         id=session["user_id"], symbol=symbol)

        # if row doesn't exist yet, create it but don't update shares

        if len(row) != 1:
            db.execute("INSERT INTO portfolio (userid, symbol) VALUES (:id, :symbol)",
                       id=session["user_id"], symbol=symbol)

        # get previous number of shares owned
        oldshares = db.execute("SELECT shares FROM portfolio WHERE userid = :id AND symbol = :symbol",
                               id=session["user_id"], symbol=symbol)
        oldshares = oldshares[0]["shares"]

        # add purchased shares to previous share number
        newshares = oldshares + shares

        # update shares in portfolio table
        db.execute("UPDATE portfolio SET shares = :newshares WHERE userid = :id AND symbol = :symbol",
                   newshares=newshares, id=session["user_id"], symbol=symbol)

        # update cash balance in users table
        db.execute("UPDATE users SET cash = :remainder WHERE id = :id",
                   remainder=remainder, id=session["user_id"])


        # update history table
        now = datetime.datetime.now()
        nows = now.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO history (userid, symbol, shares, method, price, transacted) VALUES (:userid, :symbol, :shares, 'Buy', :price, :nows)",
                   userid=session["user_id"], symbol=symbol, shares=shares, price=quote['price'], nows=nows)



    # redirect to index page
    return redirect("/exams")
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    sql = """
        select e.id, e.name, e.subject, e.level, eh.score, eh.created_time
        from exams e
        join exams_history eh on eh.exams_id=e.id
        where eh.user_id = :userid order by created_time desc
    """
    rows = db.execute(sql, userid=session["user_id"])
    print(rows)
    # return history template
    return render_template("history.html", rows=rows)
    # return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["user_name"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # if GET method, return quote.html form
    if request.method == "GET":

        # symbol = lookup("AAPL")
        # print(symbol)
        return render_template("quoted.html",symbol=[])
        # return apology("TODO")

    # if POST method, get info from form, make sure it's a valid stock
    else:

        # lookup ticker symbol from quote.html form
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        symbol = lookup(request.form.get("symbol"))

        # if lookup() returns None, it's not a valid stock symbol
        if symbol == None:
            return apology("invalid stock symbol", 400)

        # Return template with stock quote, passing in symbol dict
        return render_template("quoted.html", symbol=symbol)



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()
    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # save username and password hash in variables
        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        # Query database to ensure username isn't already taken
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)
        if len(rows) != 0:
            return apology("username is already taken", 400)

        # insert username and hash into database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                   username=username, hash=hash)

        # redirect to login page
        return redirect("/")
    else:
        return render_template("register.html")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    # if GET method, render sell.html form
    if request.method == "GET":

        # get the user's current stocks
        portfolio = db.execute("SELECT symbol FROM portfolio WHERE userid = :id",
                               id=session["user_id"])

        # render sell.html form, passing in current stocks
        return render_template("sell.html", portfolio=portfolio)

    # if POST method, sell stock
    else:
        # save stock symbol, number of shares, and quote dict from form
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        quote = lookup(symbol)
        rows = db.execute("SELECT * FROM portfolio WHERE userid = :id AND symbol = :symbol",
                          id=session["user_id"], symbol=symbol)

        # return apology if symbol invalid/ not owned
        if len(rows) != 1:
            return apology("must provide valid stock symbol", 403)

        # return apology if shares not provided. buy form only accepts positive integers
        if not shares:
            return apology("must provide number of shares", 403)

        # current shares of this stock
        oldshares = rows[0]['shares']

        # cast shares from form to int
        shares = int(shares)

        # return apology if trying to sell more shares than own
        if shares > oldshares:
            return apology("shares sold can't exceed shares owned", 403)

        # get current value of stock price times shares
        sold = quote['price'] * shares

        # add value of sold stocks to previous cash balance
        cash = db.execute("SELECT cash FROM users WHERE id = :id", id=session['user_id'])
        cash = cash[0]['cash']
        cash = cash + sold

        # update cash balance in users table
        db.execute("UPDATE users SET cash = :cash WHERE id = :id",
                   cash=cash, id=session["user_id"])

        # subtract sold shares from previous shares
        newshares = oldshares - shares

        # if shares remain, update portfolio table with new shares
        if shares > 0:
            db.execute("UPDATE portfolio SET shares = :newshares WHERE userid = :id AND symbol = :symbol",
                       newshares=newshares, id=session["user_id"], symbol=symbol)

        # otherwise delete stock row because no shares remain
        else:
            db.execute("DELETE FROM portfolio WHERE symbol = :symbol AND userid = :id",
                       symbol=symbol, id=session["user_id"])

        # update history table
        now = datetime.datetime.now()
        nows = now.strftime("%Y-%m-%d %H:%M:%S")
        db.execute("INSERT INTO history (userid, symbol, shares, method, price, transacted) VALUES (:userid, :symbol, :shares, 'Sell', :price, :nows)",
                   userid=session["user_id"], symbol=symbol, shares=shares, price=quote['price'], nows=nows)

        # redirect to index page
        return redirect("/")
        # return apology("TODO")

@app.route("/exams", methods=["GET", "POST"])
@login_required
def exams():

    sqlSuject = """
    select subject FROM exams group by subject
    """
    # print(sqlSuject)
    sujects = db.execute(sqlSuject)
    # print(sujects)
    exams = []
    examsx = db.execute("SELECT * FROM exams group by level")
    levelList = []
    for row in examsx:
        levelName = row['level']
        # print("")
        sql = "SELECT * FROM exams where level= '%s'" % levelName
        examsLevel = db.execute(sql)
        nameList=[]
        for rowLevel in examsLevel:
            name = rowLevel['name']
            # print(levelName," : ",rowLevel['name'])
            nameList.append(name)
            # print(nameList)
        tmp = {"level": levelName, "seq": nameList}
        levelList.append(tmp)

    print(levelList)

    if request.method == "POST":
        subject = request.form.get("subject")
        level = request.form.get("level")
        sql = """
                SELECT
                    e.*,
                    t1.cnt
                FROM exams e
                join (
                        select exams_id, count(*) as cnt from exams_set group by exams_id
                    ) t1 on t1.exams_id = e.id
                where subject=? and level=?
            """
        exams = db.execute(sql, subject, level )


        print("level: ", level)
        print("subject: ", subject)

    return render_template("exams.html", levelList=levelList, exams=exams, sujects=sujects)
    # return apology("TODO EXAMS")

@app.route("/examsTest/<examsId>", methods=["GET", "POST"])
@login_required
def examsTest(examsId):
    print("examsId: ", examsId)
    if request.method == "GET":
        sql = """
            select q.*
            FROM questions q
            join exams_set qs on qs.question_id=q.id
            where qs.exams_id=?
        """
        questions = db.execute(sql, examsId)
        q = []
        seq = 1
        for row in questions:
            question = row["question"]
            question = question.replace("\\\\", "\\")
            # question = question.replace("\\n", "<br>")

            c1 = row["choice1"]
            c1 = c1.replace("\\\\", "\\")

            c2 = row["choice2"]
            c2 = c2.replace("\\\\", "\\")

            c3 = row["choice3"]
            c3 = c3.replace("\\\\", "\\")

            c4 = row["choice4"]
            c4 = c4.replace("\\\\", "\\")

            row['seq'] = seq
            row['question'] = question
            choices = []
            row['choice1'] = c1
            row['choice2'] = c2
            row['choice3'] = c3
            row['choice4'] = c4
            choice = {"key":"A", "data": c1, "no":1}
            choices.append(choice)
            choice = {"key":"B", "data": c2, "no":2}
            choices.append(choice)
            choice = {"key":"C", "data": c3, "no":3}
            choices.append(choice)
            choice = {"key":"D", "data": c4, "no":4}
            choices.append(choice)
            row['choices'] = choices

            q.append(row)
            seq+=1
        # print(questions)

        return render_template("examsTest.html", questions=q, examsId=examsId)

    if request.method == "POST":
        sql = """
            select q.*
            FROM questions q
            join exams_set qs on qs.question_id=q.id
            where qs.exams_id=?
        """
        questions = db.execute(sql, examsId)
        cnt = 0
        right = 0
        question = []
        for row in questions:
            cnt += 1
            qid = row['id']
            sol = str(row['answer'])
            key = str(qid)
            text = "❌ Wrong"
            st_ans = ""
            if request.form.get(key):
                st_ans = request.form.get(key)
                st_ans = str(st_ans)
                # print(key," : ", st_ans)
                if st_ans == sol:
                    print("True")
                    right += 1
                    text = "✅ Right"

            tmp = {"no":cnt, "text": text, "sol":sol, "st_ans": st_ans}
            question.append(tmp)

        percent = (right / cnt) * 100
        print("pencent : ", percent)
        print(question)

        now = datetime.datetime.now()
        nows = now.strftime("%Y-%m-%d %H:%M:%S")
        sqlHistory = """
        insert into exams_history (user_id, exams_id, score, created_time) values
        (:user_id, :exams_id, :score, :nows)
        """

        db.execute(sqlHistory,
                   user_id=session["user_id"], exams_id=examsId, score=percent, nows=nows)

        return render_template("examsTestResult.html", examsId=examsId, percent=percent, question=question)
        # return apology("TODO POST EXAMS", examsId)