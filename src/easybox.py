import sqlite3
import bcrypt
import os
import requests
import subprocess
import argparse
import xml.etree.ElementTree as ET

DB_NAME = "users.db"
EASYBOX_FILE = "easybox"  # No .xml extension, but still XML-like

def create_user_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def create_easybox_file():
    if not os.path.exists(EASYBOX_FILE):
        root = ET.Element("easybox")
        tree = ET.ElementTree(root)
        tree.write(EASYBOX_FILE)

def register_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    if result:
        stored_hash = result[0]
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return True
    return False

def parse_easybox_file():
    if not os.path.exists(EASYBOX_FILE):
        print(f"Easybox file {EASYBOX_FILE} not found!")
        return None
    tree = ET.parse(EASYBOX_FILE)
    root = tree.getroot()
    return root

def install_dependencies(dependencies):
    for dep in dependencies.split(","):
        dep = dep.strip()
        print(f"Installing {dep}...")
        subprocess.run(dep, shell=True)

def download_raw_link(raw_link, save_path):
    response = requests.get(raw_link)
    with open(save_path, "wb") as file:
        file.write(response.content)

def containerize_application(name, dependencies, raw_link, start_cmd):
    if name:
        print(f"Containerizing application: {name}")
        install_dependencies(dependencies)
        download_raw_link(raw_link, f"{name}.tar.gz")
        print(f"Downloaded raw link to {name}.tar.gz")
        if start_cmd:
            print(f"Starting application using command: {start_cmd}")
            subprocess.run(start_cmd, shell=True)

def process_easybox_install(name, args):
    root = parse_easybox_file()
    if root is None:
        return
    for application in root.findall("application"):
        app_name = application.find("Name").text
        if app_name == name:
            dependencies = application.find("Dependencies").text
            raw_link = application.find("RawLink").text
            start_cmd = application.find("StartCMD").text if application.find("StartCMD") is not None else None
            containerize_application(name, dependencies, raw_link, start_cmd)

def main():
    create_user_table()
    create_easybox_file()

    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Arguments for the command")
    args = parser.parse_args()

    if args.command == "auth" and len(args.args) == 2:
        username, password = args.args
        register_user(username, password)
        print(f"User {username} registered successfully.")
    elif args.command == "log" and len(args.args) == 2:
        username, password = args.args
        if authenticate_user(username, password):
            print(f"Login successful for {username}.")
        else:
            print("Invalid username or password.")
    elif args.command == "easybox" and args.args and args.args[0] == "install" and len(args.args) == 3:
        app_name = args.args[1]
        process_easybox_install(app_name, args.args[2:])
    else:
        print("Invalid command or arguments.")

if __name__ == "__main__":
    main()
