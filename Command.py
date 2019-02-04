class Command:
    def __init__(self, name: str, func, usage: str):
        self.name = name
        self.func = func
        self.usage = usage

"""
        
        Abilities desired:
        * Add command to player, disable command from player
        * Command which acts on an object
        * Command which acts on the player
        
        
        :param name: 
        :param target: 
        :param type: 
"""