from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "vision_secret"

def connect_db():
    return sqlite3.connect("database.db")

# create tables
def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        snellen_score INTEGER,
        color_score INTEGER
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# register
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        conn=connect_db()
        cur=conn.cursor()

        cur.execute("INSERT INTO users(username,password) VALUES(?,?)",(username,password))
        conn.commit()

        return redirect("/")

    return render_template("register.html")

# login
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]

        conn=connect_db()
        cur=conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?",(username,password))
        user=cur.fetchone()

        if user:
            session["user"]=user[0]
            return redirect("/dashboard")

    return render_template("login.html")

# dashboard
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# vision test page
@app.route("/test")
def test():
    return render_template("eye_test.html")

# save result API
@app.route("/save_result", methods=["POST"])
def save_result():

    data=request.json

    snellen=data["snellen"]
    color=data["color"]

    conn=connect_db()
    cur=conn.cursor()

    cur.execute(
        "INSERT INTO results(user_id,snellen_score,color_score) VALUES(?,?,?)",
        (session["user"],snellen,color)
    )

    conn.commit()

    return jsonify({"message":"result saved"})


# vision history
@app.route("/history")
def history():

    conn=connect_db()
    cur=conn.cursor()

    cur.execute("SELECT snellen_score,color_score FROM results WHERE user_id=?",(session["user"],))
    data=cur.fetchall()

    return jsonify(data)


# doctor recommendation
@app.route("/doctor")
def doctor():

    return jsonify({
        "doctor":"Dr. Reddy",
        "specialist":"Ophthalmologist",
        "hospital":"City Eye Hospital"
    })


if __name__=="__main__":
    app.run(debug=True)