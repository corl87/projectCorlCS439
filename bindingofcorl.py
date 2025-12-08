import pygame, simpleGE, random, math

""" tileCollision.py
    demonstrate basic tbw 
    tile images from lpc Atlas - openGameArt
    http://opengameart.org/content/lpc-tile-atlas
    """
   
class LblOutput(simpleGE.Label):
    def __init__(self):
        super().__init__()
        self.center = (320, 25)
        self.text = "current tile: "
        self.fgColor = "white"
        self.bgColor = "black"
        self.clearBack = True
        
class Powerup(simpleGE.Sprite):
    def __init__(self, scene):
        super().__init__(scene)
        self.powerupType = 'fastAttack'
        
    def affectPlayer(self, scene):
        scene.player.powerups.append(self)
        if(self.powerupType == 'fastAttack'):
            scene.player.fireRate /= 2
        if(self.powerupType == 'lessSpread'):
            for bullet in scene.bullets:
                bullet.spread /= 2
    
class Bullet(simpleGE.Sprite):
    def __init__(self, scene, parent, damage):
        super().__init__(scene)
        self.parent = parent
        self.colorRect("white", (5, 5))
        self.setBoundAction(self.HIDE)
        self.hide()
        self.spread = 10
        self.timeShot = pygame.time.get_ticks()
        #self.bulletLife = 2000

    def fire(self):
        self.show()
        self.position = self.parent.position
        spread = random.uniform(-self.spread, self.spread) #degrees
        self.moveAngle = self.parent.imageAngle + spread
        self.speed = 10
        
class Player(simpleGE.Sprite):
    def __init__(self, scene):
        super().__init__(scene)
        self.setImage('player.png')
        self.moveSpeed = 5
        self.bulletDamage = 1
        self.tileOver = (0,0)
        self.tileState = 0
        self.fireRate = 1000 # time in milliseconds
        self.lastShot = 0 # time of last bullet
        self.powerups = []
        self.firstIteration= True

    def process(self):
        #player movement
        if self.isKeyPressed(pygame.K_w):
            self.y -= self.moveSpeed
            self.setAngle(90)
        if self.isKeyPressed(pygame.K_s):
            self.y += self.moveSpeed
            self.setAngle(-90)
        if self.isKeyPressed(pygame.K_a):
            self.x -= self.moveSpeed
            self.setAngle(180)
        if self.isKeyPressed(pygame.K_d):
            self.x += self.moveSpeed
            self.setAngle(0)
            
        #bullet motion
        if self.isKeyPressed(pygame.K_UP):
            self.setAngle(90)
            self.tryShoot()
        if self.isKeyPressed(pygame.K_DOWN):
            self.setAngle(-90)
            self.tryShoot()
        if self.isKeyPressed(pygame.K_LEFT):
            self.setAngle(180)
            self.tryShoot()
        if self.isKeyPressed(pygame.K_RIGHT):
            self.setAngle(0)
            self.tryShoot()
            
        if self.tileState == 0:
            self.moveSpeed = 3
        if self.tileState == 1:
            self.moveSpeed = 5
        if self.tileState == 2:
            self.moveSpeed = 1
        
        while(self.firstIteration):
            self.loadPlayer()
            self.firstIteration = False
            
    def loadPlayer(self):
        for powerup in self.powerups:
            if(powerup == 'fastAttack'):
                self.fireRate /= 2
            if(powerup == 'lessSpread'):
                self.fireRate /= 2
            
    def tryShoot(self):
        now = pygame.time.get_ticks()
        if now - self.lastShot >= self.fireRate:
            self.summonBullets()
            self.lastShot = now
    

    def summonBullets(self):
        """Get next bullet and fire it."""
        self.scene.currentBullet += 1
        if self.scene.currentBullet >= self.scene.NUM_BULLETS:
            self.scene.currentBullet = 0
        self.scene.bullets[self.scene.currentBullet].fire()
        
class Enemy(simpleGE.Sprite):
    def __init__(self, scene):
        super().__init__(scene)
        self.imageList = ['maxHPEnemy.png', 'midHPEnemy.png', 'minHPEnemy.png']
        self.setImage('maxHPEnemy.png')
        self.maxHP = 3
        self.currHP = 3
        self.moveSpeed = 1
        self.isAlive = True
        
    def damageTaken(self):
        self.currHP -= 1
        if(self.currHP <= 0):
            self.hide()
            self.isAlive = False
        else:
            # Calculate the health percentage (0.0 to 1.0)
            health_percent = self.currHP / self.maxHP
            
            # Determine which index to use based on thresholds
            if health_percent > 0.67:
                # Use index 0 (maxHPEnemy.png)
                image_index = 0
            elif health_percent > 0.34:
                # Use index 1 (midHPEnemy.png)
                image_index = 1
            else:
                # Use index 2 (minHPEnemy.png)
                image_index = 2
                
            self.setImage(self.imageList[image_index])

    def chasePoint(self, moveAngle):
        theta = moveAngle / 180.0 * math.pi # convert to radians for math
        dx = math.cos(theta) * self.moveSpeed
        dy = math.sin(theta) * self.moveSpeed
        dy *= -1        

        self.x += dx
        self.y += dy   
    def process(self):
        self.chasePoint(self.dirTo(self.scene.player.position))
        if self.collidesWith(self.scene.player):
            self.scene.playerDiedAt(self.scene)
        print(self.scene.levelDiedAt)
class Tile(simpleGE.Sprite):
    def __init__(self, scene):
        super().__init__(scene)
        self.images = [
            pygame.image.load("grass.png"),
            pygame.image.load("dirt.png"),
            pygame.image.load("water.png"),
            pygame.image.load("door.png")]
        
        self.stateName = ["grass", "dirt", "water", "door"]
        
        self.setSize(32, 32)
        self.GRASS = 0
        self.DIRT = 1
        self.WATER = 2
        self.DOOR = 3
        self.state = self.GRASS
        self.clicked = False
        self.active = False
        
    def setState(self, state):
        self.state = state
        self.copyImage(self.images[state])

    def process(self):
            
        # look for player
        if self.collidesWith(self.scene.player):
            stateInfo = self.stateName[self.state]
            self.scene.player.tileOver = self.tilePos
            self.scene.player.tileState = self.state
            rowCol = f"{self.tilePos[0]}, {self.tilePos[1]}"
            
            self.scene.lblOutput.text = f"{stateInfo} {rowCol}"
            
class Game(simpleGE.Scene):
    def __init__(self):
        super().__init__()
        self.setCaption("Click on a tile to edit, arrows to move")
        self.tileset = []
        
        self.ROWS = 15
        self.COLS = 20
        self.player = Player(self)
        #self.player = main.player
        self.lblOutput = LblOutput()
        self.levelDiedAt = []
        
        self.enemyList = [Enemy(self)]
        
        self.powerup = Powerup(self)
        self.powerup.powerupType = 'fastAttack'
        self.powerup.hide()
        
        self.NUM_BULLETS = 100
        self.currentBullet = 0       
        self.bullets = []
        for i in range(self.NUM_BULLETS):
            self.bullets.append(Bullet(self, self.player, self.player.bulletDamage))
        
        
        self.sprites = [self.tileset, self.player, self.lblOutput, self.bullets,
                        self.enemyList, self.powerup]
        
    def loadMap(self):
    
      for row in range(self.ROWS):
          self.tileset.append([])
          for col in range(self.COLS):
            currentVal = self.map[row][col]
            newTile = Tile(self)
            newTile.setState(currentVal)
            newTile.tilePos = (row, col)
            xPos = 16 + (32 * col)
            yPos = 16 + (32 * row)
            newTile.x = xPos
            newTile.y = yPos
            self.tileset[row].append(newTile)
    def playerPowerups(self, powerups):
        self.player.powerups = powerups 
        
    def playerDiedAt(self, playerDiedAt):
        self.levelDiedAt.append(playerDiedAt)
                
class Level1(Game):
    def __init__(self):
        super().__init__()
        self.map = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2],  
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2],  
            [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3]   
        ]
        self.loadMap()
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        for index, enemy in enumerate(self.enemyList):
            enemy.x = 500
            enemy.y = index * 150
    def process(self):
        if(self.player.tileState == 3 or not self.playerDiedAt):
            self.stop()
        if(self.player.collidesWith(self.powerup)):
            self.powerup.affectPlayer(self)
            self.player.powerups.append('fastAttack')
            self.powerup.hide()
            
        for enemy in self.enemyList: 
            for bullet in self.bullets:
                    if(bullet.visible and bullet.collidesWith(enemy)):
                        enemy.damageTaken()
                        #self.dropPowerup()
                        bullet.hide()   
            if(not enemy.isAlive):
                self.enemyList.remove(enemy)
            if(not self.enemyList): # in python an empty list is a bool false
                self.dropPowerup()

    def dropPowerup(self):
        self.powerup.show()
        
        
class Level2(Game):
    def __init__(self):
        super().__init__()
        self.map = [ 
              
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  
              [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],  
              [1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0],  
              [0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],  
              [0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0],  
              [0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0],  
              [2,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,2],  
              [2,2,2,2,2,2,0,0,0,0,1,1,0,0,0,0,2,2,2,2],  
              [0,2,2,2,2,2,2,0,0,0,1,1,0,0,2,2,2,2,2,0],  
              [0,0,0,0,0,0,2,2,2,2,1,1,2,2,2,2,0,0,0,0],  
              [0,0,0,0,0,0,0,2,2,2,1,1,2,2,0,0,0,0,0,0],  
              [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,3],  
              [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,3],  
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  
              [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]  
          ]
        self.loadMap()
        self.powerup.powerupType = 'lessSpread'
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        for index, enemy in enumerate(self.enemyList):
            enemy.x = index * 150
            enemy.y = -500
            
    def process(self):
        if(self.player.tileState == 3 or not self.playerDiedAt):
            self.stop()
        if(self.player.collidesWith(self.powerup)):
            self.powerup.affectPlayer(self)
            self.player.powerups.append('lessSpread')
            self.powerup.hide()
            
        for enemy in self.enemyList: 
            for bullet in self.bullets:
                    if(bullet.visible and bullet.collidesWith(enemy)):
                        enemy.damageTaken()
                        #self.dropPowerup()
                        bullet.hide()   
            if(not enemy.isAlive):
                self.enemyList.remove(enemy)
            if(not self.enemyList): # in python an empty list is a bool false
                self.powerup.show()
            
class Level3(Game):
    def __init__(self):
        super().__init__()
        self.map = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
            [0,0,1,1,1,1,1,0,0,1,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,1,1,1,0,0,0,1,1,1,1,0,0,0,0,0,0,0],
            [0,0,0,0,1,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0],
            [2,2,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,0,0,3],
            [2,2,2,2,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,3],
            [2,2,2,2,0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,3],
            [0,2,2,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
        self.loadMap()
        self.powerup.powerupType = 'fastAttack'
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        self.enemyList.append(Enemy(self))
        for index, enemy in enumerate(self.enemyList):
            if(index < (len(self.enemyList)/2)):
                enemy.x = index * 150
                enemy.y = -500
            else:
                enemy.x = 500
                enemy.y = index * 100 - 500
        
    def process(self):
        if(self.player.tileState == 3 or not self.playerDiedAt):
            self.stop()
        if(self.player.collidesWith(self.powerup)):
            self.powerup.affectPlayer(self)
            self.player.powerups.append('fastAttack')
            self.powerup.hide()
            
        for enemy in self.enemyList: 
            for bullet in self.bullets:
                    if(bullet.visible and bullet.collidesWith(enemy)):
                        enemy.damageTaken()
                        #self.dropPowerup()
                        bullet.hide()   
            if(not enemy.isAlive):
                self.enemyList.remove(enemy)
            if(not self.enemyList): # in python an empty list is a bool false
                self.powerup.show()
                
class Level4(Game):
    def __init__(self):
        super().__init__()
        self.map = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0],
            [0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
            [0,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0],
            [0,1,1,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0],
            [0,0,1,1,1,1,0,0,0,0,0,1,1,0,0,0,0,0,0,0],
            [0,0,0,0,1,1,1,0,0,0,0,0,1,1,1,0,0,0,0,0],
            [2,2,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,0,3],
            [2,2,2,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,3],
            [2,2,2,2,0,0,0,1,1,1,0,0,0,0,0,0,1,1,0,3],
            [0,2,2,2,0,0,0,0,1,1,0,0,0,0,0,0,0,1,0,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        ]
        self.loadMap()
        self.powerup.powerupType = 'fastAttack'
        self.player.x = 250
        self.player.y = 250
        for i in range(20):
            self.enemyList.append(Enemy(self))
       
        for index, enemy in enumerate(self.enemyList):
            if(index < (len(self.enemyList)/2)):
                enemy.x = 50
                enemy.y = index * 45
            else:
                enemy.x = 500
                enemy.y = index * 45 - 300
        
    def process(self):
        if(self.player.tileState == 3 or not self.playerDiedAt):
            self.stop()
        if(self.player.collidesWith(self.powerup)):
            self.powerup.affectPlayer(self)
            self.player.powerups.append('fastAttack')
            self.powerup.hide()
            
        for enemy in self.enemyList: 
            for bullet in self.bullets:
                    if(bullet.visible and bullet.collidesWith(enemy)):
                        enemy.damageTaken()
                        #self.dropPowerup()
                        bullet.hide()   
            if(not enemy.isAlive):
                self.enemyList.remove(enemy)
            if(not self.enemyList): # in python an empty list is a bool false
                self.powerup.show()
                
class Level5(Game):
    def __init__(self):
        super().__init__()
        self.map = [
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,2],
            [2,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,2],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,2],
            [2,0,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,0,2],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
            [2,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,2],
            [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
        ]
        self.loadMap()
        self.powerup.powerupType = 'fastAttack'
        self.player.x = 250
        self.player.y = 250
        for i in range(20):
            self.enemyList.append(Enemy(self))
       
        for index, enemy in enumerate(self.enemyList):
            enemy.maxHP = 25
            if(index < (len(self.enemyList)/2)):
                enemy.x = 50
                enemy.y = index * 45
            else:
                enemy.x = 500
                enemy.y = index * 45 - 300
        
    def process(self):
        if(self.player.tileState == 3 or not self.playerDiedAt):
            self.stop()
        if(self.player.collidesWith(self.powerup)):
            self.powerup.affectPlayer(self)
            self.player.powerups.append('fastAttack')
            self.powerup.hide()
            
        for enemy in self.enemyList: 
            for bullet in self.bullets:
                    if(bullet.visible and bullet.collidesWith(enemy)):
                        enemy.damageTaken()
                        #self.dropPowerup()
                        bullet.hide()   
            if(not enemy.isAlive):
                self.enemyList.remove(enemy)
            if(not self.enemyList): # in python an empty list is a bool false
                self.powerup.show()
                
class EndScreen(Game):
    def __init__(self):
        super().__init__()

def main():
    #player = Player()
    level1 = Level1()
    level1.start()
    
    level2 = Level2()
    level2.playerPowerups(level1.player.powerups)
    level2.playerDiedAt(level1.levelDiedAt)
    level2.start()
    
    level3 = Level3()
    level3.playerPowerups(level2.player.powerups)
    level3.playerDiedAt(level2.levelDiedAt)
    level3.start()
    
    level4 = Level4()
    level4.playerPowerups(level3.player.powerups)
    level4.playerDiedAt(level3.levelDiedAt)
    level4.start()
    
    level5 = Level5()
    level5.playerPowerups(level4.player.powerups)
    level5.playerDiedAt(level4.levelDiedAt)
    level5.start()
    
    #endScreen = EndScreen()
    #endScreen.playerDiedAt(level5.levelDiedAt)
    #endScreen.start()
    
if __name__ == "__main__":
    main()