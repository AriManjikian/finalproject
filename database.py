from sqlalchemy import create_engine, text
import os
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

with engine.connect() as conn:
    result = conn.execute(text("Select * from user"))
    print(result.all())