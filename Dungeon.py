from Room import Room

class Dungeon:
    def __init__(self):
        # Create the rooms
        self.rooms = {
            "0,0": Room(0, 0, "* There is an old scroll sitting in the room. Perhaps this could help you understand why\
                                you are here.\n* There is a door to the south", ["0,1"]),
            "0,1": Room(0, 1, "* This room has a book.", ["0,0"])
        }

        # Assign this dungeon to all of the rooms?
        for coordinates, room in self.rooms.items():
            room.dungeon = self
