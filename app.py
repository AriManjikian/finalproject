from flask import Flask, redirect, render_template, request, session, url_for, abort
from sqlalchemy import text
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from database import login_required, get_user, insert_user, get_items, get_favorites, upload_favorite, upload_cart, get_cart_items, get_username, remove_item, get_id, get_search_items, delete_cart

import stripe

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51NBrykBg5en1o2hXCnljwhfUO25fiWK8hTAPhWc0UzqROBnF6owGkHTSMEnCLp9gQqMYVAQJHg8ysFNsjv0W2QgC00tcBediuj'
app.config['STRIPE_SECRET_KEY'] = 'sk_test_51NBrykBg5en1o2hXTSap4PEk3WDEsHC4znBpHeLQG129heMlKFPnYLTC7lYRyAmH6ThewEspDn28cYlTpKYUbCjB00yieXrjMW'

stripe.api_key = app.config['STRIPE_SECRET_KEY']

Session(app)
count = 0
#-------------
#INDEX
@app.route("/")
@login_required
def index():
   #favorite
   items=get_items()
   favorites = get_favorites()
   if not favorites:
       for item in items:
           item['class'] = "bi bi-heart fa-9x"
   for item in items:
       for favorite in favorites:
           if item["item_id"] == favorite:
               item['class'] = "bi bi-heart-fill text-danger fa-9x"
               break
           item['class'] = "bi bi-heart fa-9x"
   #cart
   cart_cards = []
   total = 0
   cart_items = get_cart_items()
   cartItemList = get_items()
   for item in cartItemList:
       for cart_item in cart_items:
           if cart_item["price"] == item["price"]:
               cart_cards.append(item)
               total += float(item["price"][1:])
   total = '$' + str(total)
    #username
   username = get_username(session["user_id"])
   print(f'USERNAME---------------- {username}')
   return render_template("home.html", items=items,username=username, cart=cart_cards, total=total)


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
            session["user_id"] = get_id(username)
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


#---------------------------
#STRIPE PAYMENT CHECKOUT
@app.route("/stripe_pay")
def stripe_pay():
    cart_items = get_cart_items()
    stripe_items = []
    for cart_item in cart_items:
        stripe_items.append({
            "price": cart_item['price_id'],
            "quantity": 1
        })
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=stripe_items,
        mode='payment',
        success_url=url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('index', _external=True),
    )
    return {
        'checkout_session_id': session['id'], 
        'checkout_public_key': app.config['STRIPE_PUBLIC_KEY']
    }


#------------------------
#THANK YOU PAGE
@app.route('/thanks')
def thanks():
    items = get_items()
    cart_items = get_cart_items()
    checkout_items= []
    for cart_item in cart_items:
        for item in items:
            print(item["item_id"])
            print(cart_item["item_id"])
            if cart_item["item_id"] == item["item_id"]:
                checkout_items.append(item)
    print(checkout_items)
    return render_template('thanks.html', checkout_items=checkout_items)

    print(item['item_id'])
#--------------------------
#FAVORITES
@app.route("/favorites/<id>", methods = ["POST"])
def favorites(id):
    upload_favorite(id)
    return redirect("/")

@app.route("/favorites")
def navbar_fav():
    favorites = get_favorites()
    items=get_items()
    favorite_cards = []
    for item in items:
       for favorite in favorites:
           if item["item_id"] == favorite:
               favorite_cards.append(item)
    cart_cards = []
    total = 0
    cart_items = get_cart_items()
    cartItemList = get_items()
    for item in cartItemList:
       for cart_item in cart_items:
           if cart_item["price"] == item["price"]:
               cart_cards.append(item)
               total += float(item["price"][1:])
    total = '$' + str(total)
    username = get_username(session["user_id"])
    return render_template("favorite.html", username=username, cart=cart_cards, total=total, favorites=favorite_cards)

#--------------------
#CART ITEMS
@app.route("/cart/<id>", methods = ["POST"])
def cart(id):
    upload_cart(id)
    return redirect("/")

@app.route("/remove/<id>", methods = ["POST"])
def remove(id):
    remove_item(id)
    return redirect("/")

@app.route("/search")
def search():
    search = request.args.get("search")
    items = get_search_items(search)
    favorites = get_favorites()
    if not favorites:
       for item in items:
           item['class'] = "bi bi-heart fa-9x"
    for item in items:
       for favorite in favorites:
           if item["item_id"] == favorite:
               item['class'] = "bi bi-heart-fill text-danger fa-9x"
               break
           item['class'] = "bi bi-heart fa-9x"
   #cart
    cart_cards = []
    total = 0
    cart_items = get_cart_items()
    cartItemList = get_items()
    for item in cartItemList:
       for cart_item in cart_items:
           if cart_item["price"] == item["price"]:
               cart_cards.append(item)
               total += float(item["price"][1:])
    total = '$' + str(total)
    #username
    username = get_username(session["user_id"])
    print(f'USERNAME---------------- {username}')
    return render_template("home.html", items=items,username=username, cart=cart_cards, total=total)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)