from tags import Tag
from db import db 

def get_ingredients(doc):
    ingredients = []
    try:
        if ',' in doc['ingredients']:
            doc['ingredients'].split(',')
            for i in doc['ingredients'].split(','):
                ingredients.append(i.split(":")[0].strip())
        else:
            ingredients.append(doc['ingredients'].split(":")[0])
    except:
        pass
    return ingredients

def priority_by_system(ingredients: list[str], recipe: dict) -> tuple: 
    ''' Return a tuple of integers that represent the priority of the recipe 
        based on the number of matches on the input ingredients
    '''
    # Get the number of matching ingredients  
    recipe_ingredients: list[str] = get_ingredients(recipe)
    common_ingredients = set(ingredients).intersection(set(recipe_ingredients))

    # Get the number of missing ingredients from the recipe
    num_missing = len(set(recipe)) - len(common_ingredients)

    # Take all the scores into account 
    scores = (len(common_ingredients), -num_missing)
    return scores

def priority_by_user(tags: Tag, recipe) -> tuple: 
    ''' Return a tuple of integers that represent the priority of the recipe 
        based on the user's preferences. 
    '''
    # all = db.collection.find({ tags: { $exists: tag[0] } })
    return 

def get_recommendations(ingredients: list[str]) -> list[dict]: 
    ''' Return a list of recipes sort be the degree of matching '''
    recipes = []
    for recipe in db.collection.find(): # doc: dict
        recipe["_id"] = str(recipe["_id"])
        recipes.append(recipe)
    recipes.sort(key=lambda recipe: priority_by_system(ingredients, recipe), reverse=True)
    return recipes 