from flask import Flask, redirect, render_template, request, session
from sqlalchemy import text
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from database import login_required, get_user, insert_user

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#-------------
#INDEX
@app.route("/")
@login_required
def index():
   return render_template("home.html")


#----------------
#LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not request.form.get("username"):
            return ("must provide username")
        
        elif not request.form.get("password"):
            return ("must provide password")
        
        user = get_user(username)
        if not user:
            return "invalid user"
        elif not check_password_hash(user[0]["password_hash"], password):
            return "invalid password"
        session["user_id"] = user[0]["id"]
        return redirect("/")  
    
    else:
        return render_template("login.html")

#--------------------
#SIGNUP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        if not request.form.get("username"):
            return ("must provide username")
        
        elif not request.form.get("password"):
            return ("must provide password")
        
        elif not request.form.get("confirm"):
            return("must provide password confirmation")
        elif not request.form.get("email"):
            return("must provide email")
        
        rows = get_user(username)
        if not rows and password == confirm:
            insert_user(username, email, generate_password_hash(password))
            session["user_id"] = id
            print("id")
            print(session["user_id"])
            return redirect("/")
        else:
            return("username already in use")
    else:
        return render_template("signup.html")






if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)