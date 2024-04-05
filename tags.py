from enum import Enum

class DietaryRequirement(Enum): 
    GLUTEN_FREE = "gluten free"
    LACTOSE_FREE = "lactose free"
    NUT_FREE = "nut free"
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"

class Region(Enum): 
    # this can be an enum type in the database?  
    AUSTRALIAN = "Australian"
    CHINESE = "Chinese"
    FRENCH = "French"
    INDIAN = "Indian"
    ITALIAN = "Italian"
    JAPANESE = "Japanese"
    KOREAN = "Korean"
    MALAYSIAN = "Malaysian"
    # add more if required - maybe we should make this a bit more dynamic 

class Tag: 
    def __init__(self, tag: DietaryRequirement | Region) -> None:
        self.tag = tag


    
    