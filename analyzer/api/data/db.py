import sqlite3

from api.data.types import DataType

DB_NAME = "rag_app.db"



def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_application_logs():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS application_logs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     session_id TEXT,
                     user_query TEXT,
                     gpt_response TEXT,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()


def create_document_tables():
    conn = get_db_connection()
    for data_type in DataType:
        table_name = f"document_store_{data_type.name.lower()}"
        conn.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         filename TEXT,
                         upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.close()


def insert_application_logs(session_id, user_query, gpt_response):
    conn = get_db_connection()
    conn.execute('INSERT INTO application_logs (session_id, user_query, gpt_response) VALUES (?, ?, ?)',
                 (session_id, user_query, gpt_response))
    conn.commit()
    conn.close()


def get_chat_history(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_query, gpt_response FROM application_logs WHERE session_id = ? ORDER BY created_at',
                   (session_id,))
    messages = []
    for row in cursor.fetchall():
        messages.extend([
            {"role": "human", "content": row['user_query']},
            {"role": "ai", "content": row['gpt_response']}
        ])
    conn.close()
    return messages


def insert_document_record(filename, data_type: DataType):
    conn = get_db_connection()
    cursor = conn.cursor()
    table_name = f"document_store_{data_type.name.lower()}"
    cursor.execute(f'INSERT INTO {table_name} (filename) VALUES (?)', (filename,))
    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id


def delete_document_record(file_id, data_type: DataType):
    conn = get_db_connection()
    table_name = f"document_store_{data_type.name.lower()}"
    conn.execute(f'DELETE FROM {table_name} WHERE id = ?', (file_id,))
    conn.commit()
    conn.close()
    return True


def get_all_documents(data_type: DataType = None):
    conn = get_db_connection()
    cursor = conn.cursor()

    if data_type is None:
        # Get documents from all tables
        documents = []
        for dtype in DataType:
            table_name = f"document_store_{dtype.name.lower()}"
            cursor.execute(
                f'SELECT id, filename, upload_timestamp, ? as data_type FROM {table_name} ORDER BY upload_timestamp DESC',
                (dtype.name,))
            documents.extend(cursor.fetchall())
    else:
        # Get documents from specific table
        table_name = f"document_store_{data_type.name.lower()}"
        cursor.execute(
            f'SELECT id, filename, upload_timestamp, ? as data_type FROM {table_name} ORDER BY upload_timestamp DESC',
            (data_type.name,))
        documents = cursor.fetchall()

    conn.close()
    return [dict(doc) for doc in documents]


def get_documents_by_type(data_type: DataType):
    return get_all_documents(data_type)


create_application_logs()
create_document_tables()