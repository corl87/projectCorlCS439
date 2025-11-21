# projectCorlCS439

The goal of this project is to make a top down twin stick shooter game that works on the arcade machines.
The game will be written in python using simpleGE

To start my project I used the tileset example earlier shown in class. It was pretty easy to get a custom character model, impliment bullets, and a basic enemy which moves towards the player.
The place where I first got truly stuck was trying to make multiple levels. Making the level data itself was not hard, but getting the level to load properly is where the trouble began.
Adding a door tile was not difficult, i simply renamed the water tiles to door and added a method to their process where if they were touched they called loadMap() through scene. I abstracted the mapdata to an attribute of Game so that it could be easily referenced in loadMap(). Calling loadMap() does not display the new level even though I updated its mapdata attribute to hold the new map.
