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

def get_user(username):
    with engine.connect() as conn:
        result = conn.execute(text(f"select * from user where username = '{username}'"))
        column_names = result.keys()

        result_dicts = []

        for row in result.all():
            result_dicts.append(dict(zip(column_names, row)))

        print(result_dicts)
        return(result_dicts)
    
def insert_user(username, email, password_hash):
    with engine.connect() as conn:
        conn.execute(text(f"INSERT into user (username, email, password_hash) values ('{username}', '{email}', '{password_hash}')"))

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

        print(final_result)
        return final_result

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