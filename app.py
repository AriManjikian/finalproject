from flask import Flask, redirect, render_template, request, session, url_for, abort
from sqlalchemy import text
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from database import login_required, get_user, insert_user, get_items
import stripe

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51NBrykBg5en1o2hXCnljwhfUO25fiWK8hTAPhWc0UzqROBnF6owGkHTSMEnCLp9gQqMYVAQJHg8ysFNsjv0W2QgC00tcBediuj'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51NBrykBg5en1o2hXTSap4PEk3WDEsHC4znBpHeLQG129heMlKFPnYLTC7lYRyAmH6ThewEspDn28cYlTpKYUbCjB00yieXrjMW'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

Session(app)

#-------------
#INDEX
@app.route("/")
@login_required
def index():
   items=get_items()
   return render_template("home.html", items=items)


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
    
#--------------
#LOGOUT
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/stripe_pay")
def stripe_pay():
    items = []

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': 'price_1NC0igBg5en1o2hXV4Npyliy',
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


@app.route('/thanks')
def thanks():
    return render_template('thanks.html')



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)