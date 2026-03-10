import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

connect = psycopg2.connect(
    os.getenv("dburl")
)