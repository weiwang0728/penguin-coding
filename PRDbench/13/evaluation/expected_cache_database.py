# Expected cache and database usage example
import redis
import mysql.connector
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Redis cache connection
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# 2. Redis cache operations
def cache_recommendation(user_id, recommendations):
    key = f"rec:{user_id}"
    redis_client.setex(key, 3600, str(recommendations))  # 1 hour expiration

def get_cached_recommendation(user_id):
    key = f"rec:{user_id}"
    return redis_client.get(key)

# 3. MySQL database connection
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'recommendation_db'
}
connection = mysql.connector.connect(**mysql_config)

# 4. SQLAlchemy ORM
engine = create_engine('mysql+pymysql://user:password@localhost/recommendation_db')
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(100))

# 5. Database session
Session = sessionmaker(bind=engine)
session = Session()

# 6. Data persistence operations
def save_user_interaction(user_id, item_id, rating):
    query = "INSERT INTO interactions (user_id, item_id, rating) VALUES (%s, %s, %s)"
    cursor = connection.cursor()
    cursor.execute(query, (user_id, item_id, rating))
    connection.commit()