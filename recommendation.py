from tags import DietaryRequirement, Region
from db import db 
from collections import defaultdict
import pulp as pl   # need to "pip install pulp" on the terminal if you haven't

def get_ingredients(recipe: dict) -> list[str]:
    ''' Get all the ingredients from a recipe '''
    ingredients = []
    try:
        for ingredient in recipe['ingredients'].split(','):
            ingredients.append(ingredient.split(":")[0].strip())
    except:
        pass
    return ingredients

def get_dietary_requirements(recipe: dict) -> list[DietaryRequirement]: 
    ''' Get all the dietary requirement from a recipe '''
    requirements: list[str] = None # need to get a list of strings from the 

    return list(map(lambda x: getattr(DietaryRequirement, x), requirements))

def get_regions(recipe: dict) -> list[Region]: # or maybe not returning a list if each recipe can only have one region 
    ''' Get all the regions from a recipe '''
    regions: list[str] = None # need to get a list of strings from the 

    return list(map(lambda x: getattr(Region, x), regions))

def requirements_satisfied(requirements: list[DietaryRequirement], recipe: dict) -> bool:
    ''' Check if the recipe satisfies all the dietary requirements '''
    recipe_dietary_requirements = get_dietary_requirements(recipe) 
    for requirement in requirements: 
        if not requirement in recipe_dietary_requirements: 
            return False
    return True

def region_contained(regions: list[Region], recipe: dict) -> bool: 
    ''' Check if the recipe's region is contained in the regions specified '''
    recipe_region = get_regions(recipe)
    for region in regions: 
        if region in recipe_region: 
            return True
    return False 

def matching_scores(ingredients: list[str], recipe: dict) -> tuple: 
    ''' Return a tuple of integers that represent the priority of the recipe 
        based on the number of matches on the input ingredients
    '''
    # Get the number of matching ingredients  
    recipe_ingredients: list[str] = get_ingredients(recipe)
    common_ingredients = set(ingredients).intersection(set(recipe_ingredients))

    # Get the number of missing ingredients from the recipe
    num_missing = len(set(recipe)) - len(common_ingredients)

    # Take all the scores into account 
    scores = (-num_missing, len(common_ingredients))
    return scores

def get_meal_without_missing_ingredients(ingredients: list[str], recipes: list[dict]) -> list[dict]: 
    # store the recipes based on the ingredients they used and not used 
    # not_used = defaultdict(list)
    # used = defaultdict(list)
    # for recipe in recipes: 
    #     used_ingredients = set(get_ingredients(recipe))
    #     for ingredient in ingredients: 
    #         if not ingredient in used_ingredients: 
    #             not_used[ingredient].append(recipe)
    #         else: 
    #             used[ingredient].append(recipe)

    # def ingredients_satisfied(unused_ingredients: set[str], recipe: dict) -> bool:
    #     return set(get_ingredients(recipe)) == unused_ingredients
    
    # for recipe in recipes: 
    #     used_ingredients = set(get_ingredients(recipe))
    #     unused_ingredients = set(ingredients).difference(used_ingredients)
    #     uncheked_recipe = recipes.copy().remove(recipe)
    #     while uncheked_recipe: 
    #         next_recipe = uncheked_recipe.pop()
    #         if ingredients_satisfied(unused_ingredients, next_recipe): 

    meal_model = pl.LpProblem("Meal Making Model", pl.LpMaximize)

    # All combination of the meals using the recipes 
    possible_meals = [tuple(dishes) for dishes in pulp.allcombinations(recipes, min(len(recipes), len(ingredients)))]

    # Define a variable specifying whether the ingredients are used (0 not used, 1 used)
    ingredients_usage = pulp.LpVariable.dicts("ingredient_used", ingredients, lowBound=0, upBound=1, cat=pulp.LpInteger)
    meal_satisfied = pulp.LpVariable.dicts("meal_satisfied", possible_meals, lowBound=0, upBound=1, cat=pulp.LpInteger)

    # Specify the object for the problem - maximize the number of used ingredients 
    meal_model += pulp.lpSum([ingredients_usage[ingredient] for ingredient in ingredients])

    # Add constraints to the meal - each ingredient can only appear once  
    for meal in possible_meals: 
        if meal_satisfied[meal] == 1: 
            for ingredient in ingredients: 
                meal_model += (pulp.lpSum([ingredients_usage[ingredient] for recipe in meal if ingredient in get_ingredients(recipe)]) <= 1, f"{meal}_contains_one_{ingredient}")
            for recipe in meal: 
                for used_ingredient in get_ingredients(recipe): 
                    meal_model += ingredients_usage[used_ingredient] == 1

    meal_model.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=10))

    print("Status:----", LpStatus[meal_model.status])

    return 

def make_meal(ingredients: list[str], recipes: list[dict]) -> list[dict]:
    ''' Give a combination of dishes to make a meal based on the ingredients.

        The rules: 
        - Each ingredient should only be used in at most one recipe. 
        - If there exist one recipe that can be made without missing ingredients, 
        we should not return any recipe that contains missing ingredients. 
    '''

    # make all the valid recipes (i.e. that has at least one ingredient matching) into tuple[recipe, matching score]
    recipes_score: tuple[dict, tuple] = map(lambda r: (r, matching_scores(ingredients, r)), 
                                            list(filter(lambda r: matching_scores(ingredients, r)[1] > 0, recipes)))
    
    # sort the valid recipes based on scores 
    recipes_score.sort(key=lambda _, score: score, reverse=True)

    most_matching_recipe, most_matching_score = recipes_score[0]
    score_num_missing, score_num_matching = most_matching_score
    if abs(score_num_missing) > 0: 
        # there are no recipe that has no missing ingredients 
        
        return [most_matching_recipe]
    else: 
        # there are at least one recipe that has no missing ingredients, 
        # so don't return any recipe that has missing ingredients 
        return get_meal_without_missing_ingredients(ingredients, recipes)
    


def get_recommendation(ingredients: list[str], dietary_requirements: list[DietaryRequirement], regions: list[Region] = []) -> list[dict]: 
    ''' Return a list of recipes sort be the degree of matching '''
    all = db.collection.find()
    recipes: list[dict] = []
    for recipe in all: # recipe: dict 
        if requirements_satisfied(dietary_requirements, recipe) and region_contained(regions, recipe): 
            recipe["_id"] = str(recipe["_id"])
            recipes.append(recipe)

    
    return recipes 