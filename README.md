# projectCorlCS439

The goal of this project is to make a top down twin stick shooter game that works on the arcade machines (no mouse).
The game will be written in python using simpleGE

To start my project I used the tileset example earlier shown in class. It was pretty easy to get a custom character model, impliment bullets, and a basic enemy which moves towards the player.
The place where I first got truly stuck was trying to make multiple levels. Making the level data itself was not hard, but getting the level to load properly is where the trouble began.
Adding a door tile was not difficult, i simply renamed the water tiles to door and added a method to their process where if they were touched they called loadMap() through scene. I abstracted the mapdata to an attribute of Game so that it could be easily referenced in loadMap(). Calling loadMap() does not display the new level even though I updated its mapdata attribute to hold the new map.
Next I tried to have a game manager scene that was able to switch between tilemaps. This approach did not work for me either, after the first tilemap was loaded it refused to change.

My main issue was trying to change the tileset using one scene. The way I got this project to work was to create multiple scenes that pass attributes such as player powerups to each other.
I added powerups which change stats of the player such as spread and how fast they can shoot. I added multiple enemies to make the game get harder as you complete levels.
Getting the enemies to spawn properly was another issue, since so many different enemies are created at once and they couldnt all have the same values. I used similar logic to my waveTek project in order to properly spawn enemies.
I wanted the final level to have higher health enemies, but I didn't want to make new enemy sprites for each new section of health. My solution was to change the logic from acessing the array directly from the ammount of health, to calculating the % of max health and choosing the array element from that. 

Initally, the powerups did not transfer between levels since I made a new player for each level. I found it was possible to pass the players powerups from the previous level to start the next level.

A lot of my time in this project was spent trying to get multiple levels working. 

Using this project, you could make many differnt RPG style games, but level editing is probably this project's weakest section. Feel free to use my code to teach new students or as a demo, and I would love to see this game working on an arcade machine. 

In order to run the project, be sure all assets are present in the same folder as the main projectCorl file. In order to play the game, run projectCorl.

Since I was not in class during presentations, I will upload a video called demo where I will present my project.
