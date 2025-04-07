import sqlite3
import bcrypt
import os
import requests
import subprocess
import argparse
import xml.etree.ElementTree as ET
import json
import shutil
import hashlib
from datetime import datetime

DB_NAME = "users.db"
EASYBOX_FILE = "easybox.xml"
LOG_FILE = "install.log"
CONFIG_FILE = "easybox_config.json"
INSTALLED_APPS_DIR = "installed_apps"
METADATA_DIR = "app_metadata"

def create_dirs():
    os.makedirs(INSTALLED_APPS_DIR, exist_ok=True)
    os.makedirs(METADATA_DIR, exist_ok=True)

def create_user_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def create_easybox_file():
    if not os.path.exists(EASYBOX_FILE):
        root = ET.Element("easybox")
        tree = ET.ElementTree(root)
        tree.write(EASYBOX_FILE)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

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
        return bcrypt.checkpw(password.encode(), stored_hash.encode())
    return False

def parse_easybox_file():
    if not os.path.exists(EASYBOX_FILE):
        return None
    tree = ET.parse(EASYBOX_FILE)
    root = tree.getroot()
    return root

def calculate_file_hash_bytes(data):
    return hashlib.sha256(data).hexdigest()

def calculate_file_hash(file_path):
    with open(file_path, "rb") as f:
        return calculate_file_hash_bytes(f.read())

def install_dependencies(dependencies):
    for dep in dependencies.split(","):
        subprocess.run(dep.strip(), shell=True)

def download_raw_link(raw_link):
    response = requests.get(raw_link)
    return response.content

def is_new_version(app_name, raw_link, app_file_path):
    if os.path.exists(app_file_path):
        remote_hash = calculate_file_hash_bytes(requests.get(raw_link).content)
        local_hash = calculate_file_hash(app_file_path)
        return remote_hash != local_hash
    return True

def save_metadata(app_name, hash_value):
    metadata = {
        "name": app_name,
        "installed_at": str(datetime.now()),
        "version": hash_value,
        "runs": []
    }
    with open(os.path.join(METADATA_DIR, f"{app_name}.json"), "w") as f:
        json.dump(metadata, f, indent=2)

def update_run_history(app_name):
    path = os.path.join(METADATA_DIR, f"{app_name}.json")
    if os.path.exists(path):
        with open(path) as f:
            data = json.load(f)
        data["runs"].append(str(datetime.now()))
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

def containerize_application(name, dependencies, raw_link, start_cmd, install_path, args, dry_run):
    app_file_path = os.path.join(INSTALLED_APPS_DIR, f"{name}.tar.gz")
    if dry_run:
        print(f"[DRY RUN] Would install {name}, dependencies: {dependencies}, from: {raw_link}")
        return
    if is_new_version(name, raw_link, app_file_path):
        install_dependencies(dependencies)
        content = download_raw_link(raw_link)
        with open(app_file_path, "wb") as f:
            f.write(content)
        shutil.unpack_archive(app_file_path, install_path)
        version_hash = calculate_file_hash(app_file_path)
        save_metadata(name, version_hash)
    full_cmd = f"{start_cmd} {' '.join(args)}" if start_cmd else None
    if full_cmd:
        subprocess.run(full_cmd, shell=True)
        update_run_history(name)

def process_easybox_install(name, extra_args, config, dry_run=False):
    root = parse_easybox_file()
    if root is None:
        return
    install_path = config.get("install_path", "./")
    for app in root.findall("application"):
        if app.find("Name").text == name:
            dependencies = app.find("Dependencies").text
            raw_link = app.find("RawLink").text
            start_cmd = app.find("StartCMD").text if app.find("StartCMD") is not None else None
            containerize_application(name, dependencies, raw_link, start_cmd, install_path, extra_args, dry_run)

def rollback_installation(name):
    app_path = os.path.join(INSTALLED_APPS_DIR, f"{name}.tar.gz")
    meta_path = os.path.join(METADATA_DIR, f"{name}.json")
    if os.path.exists(app_path):
        os.remove(app_path)
    if os.path.exists(meta_path):
        os.remove(meta_path)

def list_installed_apps():
    apps = os.listdir(METADATA_DIR)
    if not apps:
        print("No applications installed.")
        return
    for app in apps:
        print(f"- {app.replace('.json', '')}")

def get_app_info(name):
    path = os.path.join(METADATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        print("App not found.")
        return
    with open(path) as f:
        data = json.load(f)
    print(json.dumps(data, indent=2))

def update_app(name, config):
    process_easybox_install(name, [], config, dry_run=False)

def log_to_file(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f"{datetime.now()}: {msg}\n")

def main():
    create_user_table()
    create_easybox_file()
    create_dirs()
    config = load_config()

    parser = argparse.ArgumentParser()
    parser.add_argument("command")
    parser.add_argument("args", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    cmd = args.command
    params = args.args

    if cmd == "auth" and len(params) == 2:
        register_user(params[0], params[1])
    elif cmd == "log" and len(params) == 2:
        if authenticate_user(params[0], params[1]):
            print("Login successful.")
        else:
            print("Login failed.")
    elif cmd in ["easybox", "eb"] and params[0] == "install" and len(params) >= 2:
        name = params[1]
        flags = [p for p in params if p.startswith("--")]
        dry = "--dry-run" in flags
        extra = [p for p in params[2:] if not p.startswith("--")]
        process_easybox_install(name, extra, config, dry)
    elif cmd in ["easybox", "eb"] and params[0] == "rollback":
        rollback_installation(params[1])
    elif cmd in ["easybox", "eb"] and params[0] == "list":
        list_installed_apps()
    elif cmd in ["easybox", "eb"] and params[0] == "info":
        get_app_info(params[1])
    elif cmd in ["easybox", "eb"] and params[0] == "update":
        update_app(params[1], config)
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()
