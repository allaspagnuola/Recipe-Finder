from tags import Tag
from db import db 

def get_ingredients(doc):
    ingredients = []
    try:
        if ',' in doc['ingredients']:
            doc['ingredients'].split(',')
            for i in doc['ingredients'].split(','):
                ingredients.append(i.split(":")[0])
        else:
            ingredients.append(doc['ingredients'].split(":")[0])
    except:
        pass
    return ingredients

def priority_by_system(ingredients: list[str], recipe: dict) -> tuple: 
    ''' Return a tuple of integers that represent the priority of the recipe 
        based on the number of matches on the input ingredients
    '''
    # Get the number of matches between the ingredients 
    recipe_ingredients: list[str] = get_ingredients(recipe)
    common_ingredients = set(ingredients + recipe_ingredients)
    return (len(common_ingredients),)

def priority_by_user(tags: Tag, recipe) -> tuple: 
    ''' Return a tuple of integers that represent the priority of the recipe 
        based on the user's preferences. 
    '''
    # all = db.collection.find({ tags: { $exists: tag[0] } })
    return 

def get_recommendations(ingredients: list[str]) -> list[dict]: 
    ''' Return a list of recipes sort be the degree of matching '''
    recipes = list(db.collection.find())
    recipes.sort(key=lambda recipe: priority_by_system(ingredients, recipe), reverse=True)
    return recipes 