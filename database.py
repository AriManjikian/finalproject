from sqlalchemy import create_engine, text
import os
from functools import wraps
from flask import session, redirect
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    os.getenv("string"),
    connect_args={
        "ssl":{
            "ssl_ca": "/etc/ssl/cert.pem"
        }
    }
    )

def get_username(id):
    with engine.connect() as conn:
        return(conn.execute(text(f"Select username from users where id = {id}")).all()[0])


def get_user(username):
    with engine.connect() as conn:
        result = conn.execute(text(f"select * from users where username = '{username}'"))
        column_names = result.keys()

        result_dicts = []

        for row in result.all():
            result_dicts.append(dict(zip(column_names, row)))
        return(result_dicts)
    
def insert_user(username, email, password_hash):
    with engine.connect() as conn:
        conn.execute(text(f"INSERT into users (username, email, password_hash) values ('{username}', '{email}', '{password_hash}')"))

def get_items():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * from item"))
        column_names = result.keys()

        result_dicts = []

        for row in result.all():
            result_dicts.append(dict(zip(column_names, row)))

        final_result = []
        for dictionary in result_dicts:
            final_result.append(dictionary)
        return final_result


def get_cart_items():
    with engine.connect() as conn:
        result = conn.execute(text(f"Select * from cart_item where user_id = {session['user_id']}"))
        column_names = result.keys()

        result_dicts = []

        for row in result.all():
            result_dicts.append(dict(zip(column_names, row)))
        final_result = []
        for dictionary in result_dicts:
            final_result.append(dictionary)
        return final_result

def get_favorites():
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT item_id from favorite where user_id = {session['user_id']}"))
        favorites_id = []
        for favlist in result.all():
            for favorite in favlist:
                favorites_id.append(favorite)
        return favorites_id

def upload_favorite(id):
    with engine.connect() as conn:
        result = conn.execute(text(f"Select * from favorite where user_id = {session['user_id']} and item_id = {id}"))
        if not result.all():
            conn.execute(text(f"INSERT INTO favorite (user_id, item_id) VALUES ({session['user_id']}, {id})"))
        else:
            conn.execute(text(f"Delete from favorite where user_id = {session['user_id']} and item_id = {id}"))
        return

def upload_cart(id):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * from item where item_id = {id}"))
        column_names = result.keys()

        result_dicts = []

        for row in result.all():
            result_dicts.append(dict(zip(column_names, row)))
        if not conn.execute(text(f"SELECT * from cart_item where user_id = {session['user_id']} and item_id={id}")).all():
            conn.execute(text(f"INSERT INTO cart_item (user_id, item_id, price, price_id) VALUES ({session['user_id']}, {id}, '{result_dicts[0]['price']}', '{result_dicts[0]['price_id']}')"))
        else:
            return

def remove_item(id):
    with engine.connect() as conn:
        conn.execute(text(f"DELETE from cart_item where user_id = {session['user_id']} and item_id = {id}"))
        return
    
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function