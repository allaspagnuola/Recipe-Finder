from tags import DietaryRequirement, Region
from db import db 
from collections import defaultdict
import pulp as pl   # need to "pip install pulp" on the terminal if you haven't; but this is not used for now

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
    requirements: list[str] = [] # need to get a list of strings from the 

    return set(map(lambda x: getattr(DietaryRequirement, x), requirements))

def get_regions(recipe: dict) -> set[Region]: # or maybe not returning a list if each recipe can only have one region 
    ''' Get all the regions from a recipe. '''
    regions: list[str] = [] # need to get a list of strings from the 

    return set(map(lambda x: getattr(Region, x), regions))

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

def ingredients_satisfied(unused_ingredients: set[str], recipe: dict) -> bool:
        return get_ingredients(recipe) == unused_ingredients

def get_meal_makable(ingredients: set[str], recipes: list[dict], meal: list[dict] = []): 
    if not recipes or not ingredients: 
        return (len(ingredients), meal)

    if ingredients_satisfied(ingredients, recipes[0]): 
        meal_using_recipe = get_meal_makable(ingredients.difference(get_ingredients(recipes[0])), recipes[1:], meal+[recipes[0]])
        meal_without_recipe = get_meal_makable(ingredients, recipes[1:], meal)
        return sorted([meal_using_recipe, meal_without_recipe])[0][-1]
    else: 
        return get_meal_makable(ingredients, recipes[1:], meal)[-1]
    
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
    
    # for recipe in recipes: 
    #     used_ingredients = set(get_ingredients(recipe))
    #     unused_ingredients = set(ingredients).difference(used_ingredients)
    #     uncheked_recipe = recipes.copy().remove(recipe)
    #     while uncheked_recipe: 
    #         next_recipe = uncheked_recipe.pop()
    #         if ingredients_satisfied(unused_ingredients, next_recipe): 

def _get_meal_without_missing_ingredients(ingredients: set[str], recipes: list[dict]) -> list[dict]: 

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

def make_meal(ingredients: set[str], recipes: list[dict]) -> list[dict]:
    ''' Give a combination of dishes to make a meal based on the ingredients.

        The rules: 
        - Each ingredient should only be used in at most one recipe. 
        - If there exist one recipe that can be made without missing ingredients, 
        we should not return any recipe that contains missing ingredients. 
    '''

    # make all the valid recipes (i.e. that has at least one ingredient matching) into tuple[recipe, matching score]
    print(recipes)
    valid_recipes = list(filter(lambda r: (matching_scores(ingredients, r)[1] > 0), recipes))
    if not valid_recipes: 
        return []
    valid_recipes_score: tuple[dict, tuple] = list(map(lambda r: (r, matching_scores(ingredients, r)), valid_recipes))
    
    return valid_recipes_score
    print("valid recipes score", valid_recipes_score)
    # sort the valid recipes based on scores 
    valid_recipes_score.sort(key=lambda x: x[1], reverse=True)

    print("recipe score", valid_recipes_score)
    most_matching_recipe, most_matching_score = valid_recipes_score[0]
    score_num_missing, _score_num_matching = most_matching_score
    if abs(score_num_missing) > 0: 
        # there are no recipe that has no missing ingredients 
        return [most_matching_recipe]
    else: 
        # there are at least one recipe that has no missing ingredients, 
        # so don't return any recipe that has missing ingredients 
        return get_meal_makable(ingredients, recipes)
    


def get_recommendation(ingredients: set[str], dietary_requirements: set[DietaryRequirement] = set(), regions: set[Region] = set()) -> list[dict]: 
    ''' Return a list of recipes sort be the degree of matching '''
    all = db.collection.find({ "ingredients": {"$exists": True} })
    recipes: list[dict] = []
    for recipe in all: # recipe: dict 
        if requirements_satisfied(dietary_requirements, recipe) and region_contained(regions, recipe): 
            recipe["_id"] = str(recipe["_id"])
            recipes.append(recipe)

    # print(recipes)
    recipes = make_meal(ingredients, recipes)

    #recipes.sort(key=lambda r: matching_scores(ingredients, r), reverse=True)
    
    return recipes 