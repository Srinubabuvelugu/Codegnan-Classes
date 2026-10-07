from pathlib import Path

# Project structure
PROJECT_NAME = ""

folders = [
    "templates",
    "static",
    "database"
]

files = [
    "README.md",
    ".gitignore",
    "requirements.txt",
    "app.py",
    "database/__init__.py",
    "database/connection.py",
    "database/tables.py",
    "database/utilsDB.py",
    "utils.py",
    ".env",
]

# Create project root
root = Path(PROJECT_NAME)
root.mkdir(exist_ok=True)
# print(root)
# Create folders
for folder in folders:
    (root / folder).mkdir(parents=True, exist_ok=True)

# Create files
for file in files:
    path = root / file
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.touch()

print(f"Project structure created successfully: {root.resolve()}")