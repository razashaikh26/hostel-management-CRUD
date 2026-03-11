import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        
    def get_connection(self):
        try:
            if self.connection is None or self.connection.closed:
                self.connection = psycopg2.connect(os.getenv("dburl"))
            return self.connection
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            self.connection = psycopg2.connect(os.getenv("dburl"))
            return self.connection
    
    def cursor(self):
        return self.get_connection().cursor()
    
    def commit(self):
        return self.get_connection().commit()
    
    def rollback(self):
        return self.get_connection().rollback()

connect = DatabaseConnection()