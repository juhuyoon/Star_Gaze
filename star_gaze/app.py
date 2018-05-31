import random, sys, copy, os, pygame
from pygame.locals import *

#parameters
FPS = 30
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
HALF_WINWIDTH = int(WINDOW_WIDTH / 2)
HALF_WINHEIGHT = int(WINDOW_HEIGHT / 2)

#tile sizes
TILEWIDTH = 50
TILEHEIGHT = 85
TILEFLOORHEIGHT = 45

#camera movements
CAM_MOVE_SPEED = 5

#decoration outside the area percentage
OUTSIDE_DECORATION_PCT = 20

BRIGHTBLUE = (0, 170, 255)
WHITE      = (255, 255, 255)
BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

#main initialization
def main():
    global FPSCLOCK, DISPLAYSURF, IMAGESDICT, TILEMAPPING, OUTSIDEDECOMAPPING, BASICFONT, PLAYERIMAGES, currentImage

    pygame.init()
    FPSCLOCK = pygame.time.Clock()

    DISPLAYSURF = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Star Gaze')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.mixer.music.load('./music/hyrule.mid')
    pygame.mixer.music.play(-1)

    #loading all of the material images, global
    IMAGESDICT = {'uncovered goal': pygame.image.load('./materials/RedSelector.png'),
                  'covered goal': pygame.image.load('./materials/Selector.png'),
                  'star': pygame.image.load('./materials/Star.png'),
                  'corner': pygame.image.load('./materials/Wall_Block_Tall.png'),
                  'wall': pygame.image.load('./materials/Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('./materials/Plain_Block.png'),
                  'outside floor': pygame.image.load('./materials/Grass_Block.png'),
                  'title': pygame.image.load('./materials/star_title.png'),
                  'solved': pygame.image.load('./materials/star_solved.png'),
                  'princess': pygame.image.load('./materials/princess.png'),
                  'boy': pygame.image.load('./materials/boy.png'),
                  'catgirl': pygame.image.load('./materials/catgirl.png'),
                  'horngirl': pygame.image.load('./materials/horngirl.png'),
                  'pinkgirl':pygame.image.load('./materials/pinkgirl.png'),
                  'rock': pygame.image.load('./materials/Rock.png'),
                  'short tree': pygame.image.load('./materials/Tree_Short.png'),
                  'tall tree': pygame.image.load('./materials/Tree_Tall.png'),
                  'ugly tree': pygame.image.load('./materials/Tree_Ugly.png')}

    #global values, dictonaries, used to create the level surfaces via representation
    #think of building tetris tiles via spacing
    TILEMAPPING = {'x': IMAGESDICT['corner'],
                   '#': IMAGESDICT['wall'],
                   'o': IMAGESDICT['inside floor'],
                   ' ': IMAGESDICT['outside floor']}

    OUTSIDEDECOMAPPING = {'1': IMAGESDICT['rock'],
                          '2': IMAGESDICT['short tree'],
                          '3': IMAGESDICT['tall tree'],
                          '4': IMAGESDICT['ugly tree']}

    #Characters the player can be
    currentImage = 0 #starts at default with princess
    PLAYERIMAGES = [IMAGESDICT['princess'],
                    IMAGESDICT['boy'],
                    IMAGESDICT['catgirl'],
                    IMAGESDICT['horngirl'],
                    IMAGESDICT['pinkgirl']]


    #start screen
    startScreen()

    levels = readLevelsFile('./levels/starPusherLevels.txt')
    currentLevelIndex = 0

    #main game loop. Goes through one level, then next level is loaded [progression]
    while True:
        # Run the level to actually start playing the game:
        result = runLevel(levels, currentLevelIndex)
        if result in ('solved', 'next'):
            # Go to the next level.
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                currentLevelIndex = 0
        elif result == 'back':
            # Go to the previous level.
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                currentLevelIndex = len(levels)-1
        elif result == 'reset':
            pass # Do nothing. Loop re-calls runLevel() to reset the level

def runLevel(levels, levelNum):
    global currentImage
    levelObj = levels[levelNum]
    mapObj = decorateMap(levelObj['mapObj'], levelObj['startState']['player']) #setting in and out tiles via map objects
    gameStateObj = copy.deepcopy(levelObj['startState']) #track the mapping of the game via copying
    mapNeedsRedraw = True #to draw the maps without ful renders
    levelSurf = BASICFONT.render('Level %s of %s' % (levelNum + 1, len(levels)), 1, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, WINDOW_HEIGHT - 35)
    mapWidth = len(mapObj) * TILEWIDTH
    mapHeight = (len(mapObj[0]) - 1) * TILEFLOORHEIGHT + TILEHEIGHT
    MAX_CAM_X_PAN = abs(HALF_WINHEIGHT - int(mapHeight / 2)) + TILEWIDTH
    MAX_CAM_Y_PAN = abs(HALF_WINWIDTH - int(mapWidth / 2)) + TILEHEIGHT

    #to set to true when finished
    levelIsComplete = False
    #camera direction
    cameraOffsetX = 0
    cameraOffsetY = 0

    #track if keys move the camera when held down:
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    #set initializations for movement
    while True:
        playerMoveTo = None
        keyPressed = False

        #exit
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            #key pressed
            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN

                #camera movement
                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'

                elif event.key == K_ESCAPE: #leave the game/quit
                    terminate()
                elif event.key == K_r: #reset the level
                    return 'reset'
                elif event.key == K_p: #change player image
                    currentImage += 1
                    if currentImage >= len(PLAYERIMAGES):
                        currentImage = 0
                    mapNeedsRedraw = True

            #to switch off the camera movement
            elif event.type == KEYUP:
                #unset the camera move mode
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

            if playerMoveTo != None and not levelIsComplete:
                #key push = movement,
                #if possible move the stars and push them around.
                moved = makeMove(mapObj, gameStateObj, playerMoveTo)

                if moved:
                    #step counter movement
                    gameStateObj['stepCounter'] += 1
                    mapNeedsRedraw = True

                if isLevelFinished(levelObj, gameStateObj):
                    #level solved, 'solved!' appears
                    levelIsComplete = True
                    keyPressed = False

            DISPLAYSURF.fill(BGCOLOR)
            #to not redraw the entire map, only redraw when something/some object changes. Keep the same object.
            if mapNeedsRedraw:
                mapSurf = drawMap(mapObj, gameStateObj, levelObj['goals'])
                mapNeedsRedraw = False

            if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
                cameraOffsetY += CAM_MOVE_SPEED
            elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
                cameraOffsetY -= CAM_MOVE_SPEED
            if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
                cameraOffsetX += CAM_MOVE_SPEED
            elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
                cameraOffsetX -= CAM_MOVE_SPEED

            #adjust map size based on camera
            mapSurfRect = mapSurf.get_rect()
            mapSurfRect.center = (HALF_WINWIDTH + cameraOffsetX, HALF_WINHEIGHT + cameraOffsetY)
            #blit = draw one image into another
            DISPLAYSURF.blit(mapSurf, mapSurfRect)

            DISPLAYSURF.blit(levelSurf, levelRect)
            stepSurf = BASICFONT.render('Steps: %s' % (gameStateObj['stepCounter']), 1, TEXTCOLOR)
            stepRect = stepSurf.get_rect()
            stepRect.bottomleft = (20, WINDOW_HEIGHT - 10)
            DISPLAYSURF.blit(stepSurf, stepRect)

            #victory graphic
            if levelIsComplete:
                solvedRect = IMAGESDICT['solved'].get_rect()
                solvedRect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)
                DISPLAYSURF.blit(IMAGESDICT['solved'], solvedRect)
                #solved shows when the conditions are met and another key is pressed after completion
                if keyPressed:
                    return 'solved'

            pygame.display.update()
            FPSCLOCK.tick()

def isWall(mapObj, x, y):
    #set up boundaries and walls where if beyond walls, return False.
    if x < 0 or x >= len(mapObj) or y < 0 or y >= len(mapObj[x]):
        return False
    elif mapObj[x][y] in ('#', 'x'):
        return True
    return False

def decorateMap(mapObj, startxy):
    #make the map, hardest part

    startx, starty = startxy
    #copy map object, don't modify the original
    mapObjCopy = copy.deepcopy(mapObj)

    #Remove the non-wall characters
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            if mapObjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapObjCopy[x][y]=' '


    #Determining inside/outside the map and floor
    floodFill(mapObjCopy, startx, starty, ' ', 'o')

    #Convert walls into corner tiles when together
    for x in range(len(mapObjCopy)):
        for y in range(len(mapObjCopy[0])):
            #to check if there is a corner wall tile. If so, it becomes a corner instead of adjacent walls.
            if mapObjCopy[x][y] == '#':
                if (isWall(mapObjCopy, x, y-1) and isWall(mapObjCopy, x+1, y)) or \
                    (isWall(mapObjCopy, x+1, y) and isWall(mapObjCopy, x, y+1)) or \
                    (isWall(mapObjCopy, x, y+1) and isWall(mapObjCopy, x-1, y)) or \
                    (isWall(mapObjCopy, x-1, y) and isWall(mapObjCopy, x, y-1)):
                        mapObjCopy[x][y] = 'x'

            elif mapObjCopy[x][y] == ' ' and random.randint(0, 99) < OUTSIDE_DECORATION_PCT:
                mapObjCopy[x][y] = random.choice(list(OUTSIDEDECOMAPPING.keys()))

    return mapObjCopy

def isBlocked(mapObj, gameStateObj, x, y): #true if position on map is blocked by wall/star
    if isWall(mapObj, x, y):
        return True
    elif x < 0 or x >= len(mapObj) or y < 0 or y > len(mapObj[x]):
        return True
    elif(x, y) in gameStateObj['stars']:
        return True
    return False

def makeMove(mapObj, gameStateObj, playerMoveTo):
    #Conditions to see if player can move. If wall/star, do not move.
    #Returns true if player moved, otherwise, return False.

    playerx, playery = gameStateObj['player']
    stars = gameStateObj['stars']

    #movement
    if playerMoveTo == UP:
        xOffset = 0
        yOffset = -1
    elif playerMoveTo == DOWN:
        xOffset = 0
        yOffset = 1
    elif playerMoveTo == RIGHT:
        xOffset = 1
        yOffset = 0
    elif playerMoveTo == LEFT:
        xOffset = -1
        yOffset = 0

    #see if player can move in that direction
    if isWall(mapObj, playerx + xOffset, playery + yOffset):
        return False
    else:
        if (playerx + xOffset, playery + yOffset) in stars:
            if not isBlocked(mapObj, gameStateObj, playerx + (xOffset * 2), playery + (yOffset * 2)):
                #moving the star
                ind = stars.index((playerx + xOffset, playery + yOffset))
                stars[ind] = (stars[ind][0] + xOffset, stars[ind][1] + yOffset)
            else:
                return False

        gameStateObj['player'] = (playerx + xOffset, playery + yOffset)
        return True

def startScreen():
    #title position
    titleRect = IMAGESDICT['title'].get_rect()
    topCoord = 50
    titleRect.top = topCoord
    titleRect.centerx = HALF_WINWIDTH
    topCoord += titleRect.height

    instructionText = ['Welcome to Star Gaze!',
                       'Use the arrow keys to move, WASD for camera control, P to change character.',
                       'R to reset level, ESC key to quit.',
                       'N for next level, B to go back a level.'
                       'Good luck!']

    #set canvas, then put title image
    DISPLAYSURF.fill(BGCOLOR)
    DISPLAYSURF.blit(IMAGESDICT['title'], titleRect)

    #positioning the text
    for i in range(len(instructionText)):
        instSurf = BASICFONT.render(instructionText[i], 1, TEXTCOLOR)
        instRect = instSurf.get_rect()
        topCoord +=10
        instRect.top = topCoord
        instRect.centerx = HALF_WINWIDTH
        topCoord += instRect.height
        DISPLAYSURF.blit(instSurf, instRect)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return

        #Display content
        pygame.display.update()
        FPSCLOCK.tick()

def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find level file: %s' % (filename)
    mapFile = open(filename, 'r') #to read
    content = mapFile.readlines() + ['\r\n'] #each file must end with blank line or it won't run.
    mapFile.close()

    levels = []
    levelNum = 0
    mapTextLines = [] #where the map's line design goes
    mapObj = [] #where the objects are made based on the lines.
    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')

        if ';' in line: #to ignore them as they are used as comments in the map build file
            line = line[:line.find(';')]

        if line != '':
            #this line is part of the map
            mapTextLines.append(line)
        elif line == '' and len(mapTextLines) > 0: #blank = end of a level's map

            maxWidth = -1
            for i in range(len(mapTextLines)):
                if len(mapTextLines[i]) > maxWidth:
                    maxWidth = len(mapTextLines[i])
            for i in range(len(mapTextLines)):
                mapTextLines[i] += ' ' * (maxWidth - len(mapTextLines[i])) #to make rectangle shape, make larger width

            for x in range(len(mapTextLines[0])):
                mapObj.append([])
            for y in range(len(mapTextLines)):
                for x in range(maxWidth):
                    mapObj[x].append(mapTextLines[y][x]) #done to represent each tile on the map.

            # The x and y for the player's starting position
            startx = None # The x and y for the player's starting position
            starty = None
            goals = [] # list of (x, y) tuples for each goal.
            stars = [] # list of (x, y) for each star's starting position.
            for x in range(maxWidth):
                for y in range(len(mapObj[x])):
                    if mapObj[x][y] in ('@', '+'):
                        # '@' is player, '+' is player & goal
                        startx = x
                        starty = y
                    if mapObj[x][y] in ('.', '+', '*'):
                        # '.' is goal, '*' is star & goal
                        goals.append((x, y))
                    if mapObj[x][y] in ('$', '*'):
                        # '$' is star
                        stars.append((x, y))

            #simple assertion testings to make sure the conditions are met for the game and level design.
            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark start point' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' %(levelNum+1, lineNum, filename, len(goals), len(stars))

            gameStateObj = {'player':(startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapObj),
                        'mapObj': mapObj,
                        'goals' : goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            #reset & initializations for next level
            mapTextLines = []
            mapObj = []
            gameStateObj = {}
            levelNum += 1
    return levels

def floodFill(mapObj, x, y, oldChar, newChar):
    #when shifting between characters using p, the same position will be met.
    #floodfill algorithm https://stackoverflow.com/questions/19839947/flood-fill-in-python

    #set initial condition
    if mapObj[x][y] == oldChar:
        mapObj[x][y] = newChar

    if x < len(mapObj) - 1 and mapObj[x+1][y] == oldChar:
        floodFill(mapObj, x+1, y, oldChar, newChar) # Check right
    if x > 0 and mapObj[x-1][y] == oldChar:
        floodFill(mapObj, x-1, y, oldChar, newChar) # Check left
    if y < len(mapObj[x]) - 1 and mapObj[x][y+1] == oldChar:
        floodFill(mapObj, x, y+1, oldChar, newChar) # Check down
    if y > 0 and mapObj[x][y-1] == oldChar:
        floodFill(mapObj, x, y-1, oldChar, newChar) # Check up

def drawMap(mapObj, gameStateObj, goals):
    #creates the map
    #puts the map surface onto mapSurf object, draws on the tiles
    mapSurfWidth = len(mapObj) * TILEWIDTH
    mapSurfHeight = (len(mapObj[0]) -1) * (TILEHEIGHT - TILEFLOORHEIGHT) + TILEHEIGHT
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(BGCOLOR)

    for x in range(len(mapObj)):
        for y in range(len(mapObj[x])):
            spaceRect = pygame.Rect((x * TILEWIDTH, y * (TILEHEIGHT - TILEFLOORHEIGHT), TILEWIDTH, TILEHEIGHT)) #go through all combinations to set floor images at right location
            if mapObj[x][y] in TILEMAPPING:
                baseTile = TILEMAPPING[mapObj[x][y]]
            elif mapObj[x][y] in OUTSIDEDECOMAPPING:
                baseTile = TILEMAPPING[' ']

            mapSurf.blit(baseTile, spaceRect)

            if mapObj[x][y] in OUTSIDEDECOMAPPING: #set outside specs to put trees and rocks for decorations
                mapSurf.blit(OUTSIDEDECOMAPPING[mapObj[x][y]], spaceRect)
            elif (x,y) in gameStateObj['stars']: #check for goal first, then put the star
                if (x,y) in goals:
                    mapSurf.blit(IMAGESDICT['covered goal'], spaceRect)
                mapSurf.blit(IMAGESDICT['star'], spaceRect)
            elif(x,y) in goals:
                mapSurf.blit(IMAGESDICT['uncovered goal'], spaceRect) #once conditions are met, put goal without the star

            #put player
            if(x,y) == gameStateObj['player']:
                mapSurf.blit(PLAYERIMAGES[currentImage], spaceRect)

    return mapSurf

def isLevelFinished(levelObj, gameStateObj):
    for goal in levelObj['goals']: #if there is a goal without a star, return false
        if goal not in gameStateObj['stars']:
            return False
    return True



def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()