class Command:
    def __init__(self, name: str, func, usage: str, example_usage: str, number_of_parameters: int):
        self.name = name
        self.func = func
        self.usage = usage
        self.example_usage = example_usage
        self.number_of_parameters = number_of_parameters

"""
        
        Abilities desired:
        * Add command to player, disable command from player
        * Command which acts on an object
        * Command which acts on the player
        
        
        :param name: 
        :param target: 
        :param type: 
"""