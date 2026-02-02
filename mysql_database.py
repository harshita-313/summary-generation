import mysql.connector
from datetime import datetime
import uuid

# Connect to server
def get_db():
     return mysql.connector.connect(
        host="127.0.0.1",
        port=3307,
        user="root",
        password="",
        database="summary_project"
    )
    
# Generate new uuid
def get_id():
    return str(uuid.uuid4())

def insert_conversation(user_id, transcript, summary):
    db = get_db()
    cur = db.cursor()

    new_id = str(uuid.uuid4())  # generate UUID inside the function
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
        INSERT INTO summary (id, user_id, transcript, summary, time)
        VALUES (%s, %s, %s, %s, %s)
    """
    values = (new_id, user_id, transcript, summary, current_time)

    cur.execute(query, values)
    db.commit()
    cur.close()
    db.close()

def insert_text(text, summary, language):
    db = get_db()
    cur = db.cursor()

    query = """
        INSERT INTO api_summary (text, summary, language)
        VALUES (%s, %s, %s)
    """
    values = (text, summary, language)
    cur.execute(query,values)
    db.commit()
    cur.close()
    db.close()

def fetch_summary(user_id, limit):
    db = get_db()
    cur = db.cursor()

    query = """
        SELECT id, user_id, transcript, summary, time
        FROM summary
        WHERE user_id = %s
        ORDER BY time DESC
        LIMIT %s
    """

    cur.execute(query, (user_id, limit))
    rows = cur.fetchall()

    cur.close()
    db.close()
    return rows

def delete_summary(id):
    db = get_db()
    cur = db.cursor()
    query = """
    DELETE FROM SUMMARY WHERE ID = %s
    """
    values = (id,)
    cur.execute(query, values)
    db.commit()
    cur.close()
    db.close()
