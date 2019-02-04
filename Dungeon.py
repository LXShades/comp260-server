from Room import Room
from Item import Item

class Dungeon:
    def __init__(self):
        # Create the rooms
        self.rooms = {
            "0,0": Room(0, 0, "This is the foyer. It's empty. You have no reason to be here, and it's extremely boring. However, a door may solve this problem.\n\n* There is a door to the south", ["0,1"]),
            "0,1": Room(0, 1, "This room appears to be some sort of manual, real-life website.", ["0,0"])
        }

        # Assign some objects to the book room
        self.rooms["0,1"].items.append(Item("Book", self.rooms["0,1"], "There is a book sitting in the corner."))

        # Assign this dungeon to all of the rooms?
        for coordinates, room in self.rooms.items():
            room.dungeon = self

    """
    Updates all necessary objects, players, etc in the dungeon
    """
    def update(self):
        for index, room in self.rooms.items():
            room.update()
