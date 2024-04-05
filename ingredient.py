class Ingredient: 
    def __init__(self, food: str, quantity: int) -> None:
        self.food = food.lower().strip() # standardize the string 
        self.quantity = quantity 