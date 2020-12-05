import selenium
from selenium import webdriver
import time
import os
import pathlib
import keyboard
import threading
import sys


driver = webdriver.Chrome("chromedriver.exe")
driver.get("https://play2048.co/")


class JS:
    filename_currentWorkingPath = pathlib.Path(__file__).parent.absolute()
    filename_getBoardScript = os.path.join(filename_currentWorkingPath, "getGrid.js")
    filename_getScoreScript = os.path.join(filename_currentWorkingPath, "getScore.js")
    filename_getLocalStorageStringScript = os.path.join(filename_currentWorkingPath, "getLocalStorageString.js")
    filename_getGameStateScript = os.path.join(filename_currentWorkingPath, "getGameState.js")

    script_getGameBoardInfo = open(filename_getBoardScript, "r").read()
    script_getScore = open(filename_getScoreScript, "r").read()
    script_getLocalStorageString = open(filename_getLocalStorageStringScript, "r").read()
    script_getGameState = open(filename_getGameStateScript, "r").read()

    global driver

    def __init__(self):
        self.driver = driver

    def executeJavaScript(self, script):
        return self.driver.execute_script(script)

    def getScore(self):
        return self.executeJavaScript(self.script_getScore)

    def getGameBoardInfo(self):
        return self.executeJavaScript(self.script_getGameBoardInfo)

    def getGameStatus(self):
        return self.executeJavaScript(self.script_getGameState)


class GameInfo:
    javaScript = JS()
    blocks = javaScript.getGameBoardInfo()
    prevDirection = "down"
    prevBlocks = blocks


class Debug:
    def printGameToConsole(self, blocks):
        for i in blocks:
            print(i)
        print("+----------+")


def getBestMovingDirection(gameInfo):
    blocks = gameInfo.blocks

    rowAmount = [0, 0, 0, 0]
    columnAmount = [0, 0, 0, 0]

    for i in range(4):
        for j in range(4):
            rowAmount[i] += blocks[i][j]
            columnAmount[j] += blocks[i][j]

    rowWithoutZero = [[0 for x in range(4)] for y in range(4)]
    columnWithoutZero = [[0 for x in range(4)] for y in range(4)]

    for i in range(4):
        for j in range(4):
            rowWithoutZero[i][j] = blocks[i][j]
            columnWithoutZero[i][j] = blocks[j][i]

    for i in range(4):
        if rowAmount[i] != 0:
            for j in range(3):
                while rowWithoutZero[i][j] == 0 and rowWithoutZero[i][j + 1] != 133:
                    for k in range(3 - j):
                        rowWithoutZero[i][j + k] = rowWithoutZero[i][j + k + 1]
                    rowWithoutZero[i][3] = 133
            for j in range(4):
                if rowWithoutZero[i][j] == 133:
                    rowWithoutZero[i][j] = 0

    for i in range(4):
        if columnAmount[i] != 0:
            for j in range(3):
                while columnWithoutZero[i][j] == 0 and columnWithoutZero[i][j + 1] != 133:
                    for k in range(3 - j):
                        columnWithoutZero[i][j + k] = columnWithoutZero[i][j + k + 1]
                    columnWithoutZero[i][3] = 133
            for j in range(4):
                if columnWithoutZero[i][j] == 133:
                    columnWithoutZero[i][j] = 0

    rowPossibleFusions = [0, 0, 0, 0]
    columnPossibleFusions = [0, 0, 0, 0]

    for i in range(4):
        for j in range(3):
            if rowWithoutZero[i][j] == rowWithoutZero[i][j + 1] and rowWithoutZero[i][j] != 0:
                rowPossibleFusions[i] += 1
            if columnWithoutZero[i][j] == columnWithoutZero[i][j + 1] and columnWithoutZero[i][j] != 0:
                columnPossibleFusions[i] += 1

    proHorizontal = 0
    proVertical = 0

    for i in range(4):
        if columnPossibleFusions[i] > rowPossibleFusions[i]:
            proVertical += 1
        else:
            if rowPossibleFusions[i] > columnPossibleFusions[i]:
                proHorizontal += 1

    if gameInfo.prevDirection == blocks:
        if gameInfo.prevDirection == "up" or gameInfo.prevDirection == "down":
            gameInfo.prevDirection = "left"
            return "left"
        else:
            gameInfo.prevDirection = "up"
            return "up"

    gameInfo.prevBlocks = blocks

    if proHorizontal == proVertical:
        for j in range(4):
            if rowAmount[j] > columnAmount[j]:
                proHorizontal += 1
            else:
                if columnAmount[j] > rowAmount[j]:
                    proVertical += 1

    if proHorizontal > proVertical:
        if gameInfo.prevDirection == "left":
            gameInfo.prevDirection = "right"
            return "right"
        else:
            gameInfo.prevDirection = "left"
            return "left"
    else:
        if gameInfo.prevDirection == "up":
            gameInfo.prevDirection = "down"
            return "down"
        else:
            gameInfo.prevDirection = "up"
            return "up"


def moveInDirection(direction):
    if direction == "up":
        keyboard.press_and_release('w')
    if direction == "down":
        keyboard.press_and_release('s')
    if direction == "left":
        keyboard.press_and_release('a')
    if direction == "right":
        keyboard.press_and_release('d')


def refreshBlocks():
    script = JS()
    return script.getGameBoardInfo()


def retry():
    print("continue? [Y/N]")

    keyboardInput = sys.stdin.read(1)

    if keyboardInput == 'y' or keyboardInput == 'Y':
        return True
    else:
        if keyboardInput == 'n' or keyboardInput == 'N':
            return False


class KeyboardInputHandler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.keypress = threading.Event()

    def run(self):
        while True:
            if keyboard.is_pressed("w"):
                self.keypress.set()
            else:
                self.keypress.clear()


class MovingDirectionHandler(threading.Thread):
    def __init__(self, game):
        threading.Thread.__init__(self)
        self.game = game
        self.finished = threading.Event()
        self.direction = game.prevDirection

    def calculate(self):
        if not self.finished.isSet():
            self.direction = getBestMovingDirection(self.game)
            self.finished.set()
        else:
            return

    def run(self):
        self.calculate()


def main():
    timeTmp = time.process_time()
    delay = 0.1

    game = GameInfo()

    thread_keyboardInput = KeyboardInputHandler()
    thread_keyboardInput.start()
    thread_calculateMovingDirection = MovingDirectionHandler(game)
    thread_calculateMovingDirection.start()


    while True:
        try:
            _ = driver.window_handles
            if driver.find_element_by_class_name("retry-button").is_displayed():
                if retry():
                    keyboard.press_and_release('r')
                else:
                    driver.quit()
                    exit()
        except BaseException:
            print("exiting")
            driver.quit()
            exit()

        if thread_keyboardInput.keypress.isSet():
            game.blocks = refreshBlocks()
        if time.process_time() >= timeTmp + delay:
            timeTmp = time.process_time()

            thread_calculateMovingDirection.finished.wait()
            direction = thread_calculateMovingDirection.direction

            moveInDirection(direction)

            game.blocks = refreshBlocks()

            thread_calculateMovingDirection.finished.clear()
            thread_calculateMovingDirection.calculate()


if __name__ == "__main__":
    main()
