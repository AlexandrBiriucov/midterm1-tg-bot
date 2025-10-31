import os

DB_PATH = r"C:\telegram-gym-bot\main\feature\dev3-progress-stats\stats.db"

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Database file deleted!")
else:
    print("Database file does not exist.")
