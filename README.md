# Recipe Finder
A project for 2024 codebrew hackathon. Presented by team Not yet awake.

## The problem

People usually have leftover ingredients at home, and we want to use up the ingredients before they go bad.



## Our Goal

Figuring out what can be made with the available ingredients.



## Features

1. User can register their own account and log in, log out.
2. On home page, user can input some ingredients and requirements and we can return our recommended recipe based on what user have input.
3. User can also add their own favorite recipes into our own database.



Our rules determining the recommendation: 

​    \- Each ingredient should only be used in at most one recipe. 

​    \- If there exist one recipe that can be made without missing ingredients, we should not return any recipe that contains missing ingredients. 

​    \- If there are no recipe that is makable, return all recipes that have at least one ingredients specified by the user 



## Plan for Future 

1. An user profile page that user can input their preference.
2. User's rating on recipes.
3. For recipes we can also add the methods how they can be made. 
4.  Provide links to supermarkets if they are missing ingredients.