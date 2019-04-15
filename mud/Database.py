import sqlite3
import json

from Item import Item

"""Handles persistent data in the game, including accounts, etc"""

class Database:
    account_db = None
    room_db = None
    player_db = None
    item_db = None

    item_definitions = {}

    @staticmethod
    def startup():
        # Load the SQL databases
        Database.account_db = sqlite3.connect("accounts.db")
        Database.room_db = sqlite3.connect("rooms.db")
        Database.player_db = sqlite3.connect("players.db")
        Database.item_db = sqlite3.connect("items.db")

        # Create account tables if they don't exist
        Database.account_db.execute("CREATE TABLE IF NOT EXISTS player_accounts(name, passhash, salt)")
        Database.room_db.execute("CREATE TABLE IF NOT EXISTS rooms(title, description, connections, items)")
        Database.player_db.execute("CREATE TABLE IF NOT EXISTS players(account_name, character_name, last_room)")
        Database.item_db.execute("CREATE TABLE IF NOT EXISTS items(id, name, entry_description, commands)")

        # Load items into the item definitions
        cursor = Database.item_db.execute("SELECT * FROM items")
        items = cursor.fetchall()

        for item in items:
            Database.item_definitions[item[0]] = Item(item[1], item[2], Database.read_json(item[3]))

    @staticmethod
    def shutdown():
        # Save and disconnect databases
        Database.account_db.commit()
        Database.account_db.close()

        Database.room_db.commit()
        Database.room_db.close()

        Database.player_db.commit()
        Database.player_db.close()

        Database.item_db.commit()
        Database.item_db.close()

    """Provides a safe method to dump json from the database"""
    @staticmethod
    def read_json(string):
        return json.loads(str.replace(str.replace(string, "\r", ""), "\n", ""))
