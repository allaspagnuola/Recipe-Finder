from tags import DietaryRequirement, Region
from db import db 
from collections import defaultdict


def get_ingredients(recipe: dict) -> set[str]:
    ''' Helper function. Get all the ingredients from a recipe. '''
    ingredients = []
    try:
        for ingredient in recipe['ingredients'].split(','):
            ingredients.append(ingredient.split(":")[0].strip())
    except:
        pass
    return set(ingredients)


def get_dietary_requirements(recipe: dict) -> set[DietaryRequirement]: 
    ''' Get all the dietary requirements from a recipe. '''
    dietary_requirement = []
    try:
        for dr in recipe['dietary_requirements']:
            dietary_requirement.append(set(map(lambda x: getattr(DietaryRequirement, x), dr)))
    except:
        pass
    return set(dietary_requirement)


def get_regions(recipe: dict) -> set[Region]: # or maybe not returning a list if each recipe can only have one region 
    ''' Get all the regions from a recipe. '''
    regions=recipe["cuisine"] # need to get a list of strings from the 

    return set([Region[regions].value])


def requirements_satisfied(requirements: set[DietaryRequirement], recipe: dict) -> bool:
    ''' Check if the recipe satisfies all the dietary requirements '''
    recipe_dietary_requirements = get_dietary_requirements(recipe) 
    for requirement in requirements: 
        if not requirement in recipe_dietary_requirements: 
            return False
    return True


def region_contained(regions: set[Region], recipe: dict) -> bool: 
    ''' Check if the recipe's region is in the selection if there regions specified '''
    if not regions: 
        return True
    recipe_region = get_regions(recipe)
    for region in regions: 
        if region in recipe_region: 
            return True
    return False 


def matching_scores(ingredients: set[str], recipe: dict) -> tuple[int, int]: 
    ''' Return a tuple of integers (number-of-missing-ingredients, number-of-matching-ingredients) 
        that represent the priority of the recipe.

        When sorting, we should set reverse=True to get the most matching recipe at the start. 
    '''
    # Get the number of matching ingredients  
    def standardize_ingredients(ingredients): 
        return set(map(lambda x: ''.join(x.split()).lower(), ingredients))
    ingredients = standardize_ingredients(ingredients)
    recipe_ingredients = standardize_ingredients(get_ingredients(recipe))
    common_ingredients = ingredients.intersection(recipe_ingredients)

    # Get the number of missing ingredients from the recipe
    num_missing = len(recipe_ingredients) - len(common_ingredients)

    # Take all the scores into account 
    scores = (-num_missing, len(common_ingredients))
    return scores


def ingredients_satisfied(ingredients: set[str], recipe: dict) -> bool:
        ''' Return True if the recipe can be made by the ingredients, else return False '''
        return matching_scores(ingredients, recipe)[0] == 0


def get_meal_makable(ingredients: set[str], recipes: list[dict], meal: list[dict] = []): 
    if not recipes or not ingredients: 
        return (len(ingredients), meal)

    if ingredients_satisfied(ingredients, recipes[0]): 
        meal_using_recipe = get_meal_makable(ingredients.difference(get_ingredients(recipes[0])), recipes[1:], meal+[recipes[0]])
        meal_without_recipe = get_meal_makable(ingredients, recipes[1:], meal)
        return sorted([meal_using_recipe, meal_without_recipe])[0]
    else: 
        return get_meal_makable(ingredients, recipes[1:], meal)


def make_meal(ingredients: set[str], recipes: list[dict]) -> list[dict]:
    ''' Give a combination of dishes to make a meal based on the ingredients.

        The rules: 
        - Each ingredient should only be used in at most one recipe. 
        - If there exist one recipe that can be made without missing ingredients, 
        we should not return any recipe that contains missing ingredients. 
        - If there are no recipe that is makable, return all recipes that have 
        at least one ingredients specified by the user 
    '''

    # Make all the valid recipes (i.e. that has at least one ingredient matching) into tuple[recipe, matching score]
    valid_recipes = list(filter(lambda r: (matching_scores(ingredients, r)[1] > 0), recipes))
    if not valid_recipes: 
        return []
    valid_recipes_score: tuple[dict, tuple] = list(map(lambda r: (r, matching_scores(ingredients, r)), valid_recipes))
    
    # Sort the valid recipes based on scores 
    valid_recipes_score.sort(key=lambda x: x[1], reverse=True)

    # To understand `num_missing`: 
    #   valid_recipes_score[0] == highest scored recipe 
    #   valid_recipes_score[0][1] == the score of the highest scored recipe 
    #   valid_recipes_score[0][1][0] == the number of missing ingredients of the highest scored recipe (in neg value)
    num_missing = abs(valid_recipes_score[0][1][0])

    if num_missing > 0: 
        # there are no recipe that has no missing ingredients 
        return list(map(lambda recipe_score: recipe_score[0], valid_recipes_score))
    else: 
        # there are at least one recipe that has no missing ingredients, 
        # so don't return any recipe that has missing ingredients 
        return get_meal_makable(ingredients, recipes)[-1]
    

def get_recommendation(ingredients: set[str], dietary_requirements: set[DietaryRequirement] = set(), regions: set[Region] = set()) -> list[dict]: 
    ''' Return a list of recipes sort be the degree of matching '''

    # get all the data that has the field "ingredients"
    all = db.collection.find({ "ingredients": {"$exists": True} })

    # filter out the recipe matches the tags (i.e. dietary_requirements & regions)
    recipes: list[dict] = []
    for recipe in all: 
        if requirements_satisfied(dietary_requirements, recipe) and region_contained(regions, recipe): 
            recipe["_id"] = str(recipe["_id"])
            recipes.append(recipe)

    recipes = make_meal(ingredients, recipes)
    
    return recipes 