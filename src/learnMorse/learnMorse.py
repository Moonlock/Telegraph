#! /usr/bin/python3

import random
import subprocess

from learnMorse.alphabet import morse
from symbols import Symbol
from threading import Timer
from time import sleep

CHAR_WPM = 20
OVERALL_WPM = 10
NUM_CHARS = 2

COUNTS_PER_WORD = 50
MS_PER_MINUTE = 60000
MS_PER_COUNT = MS_PER_MINUTE / (COUNTS_PER_WORD * CHAR_WPM)

ta = (60*CHAR_WPM - 37.2*OVERALL_WPM) / (CHAR_WPM * OVERALL_WPM)
ts = 1.0 / (CHAR_WPM/60.0 * COUNTS_PER_WORD)
tc = 3*ta / 19 - ts
tw = 7*ta / 19 - ts

def dit():
    subprocess.call(["paplay", "learnMorse/sounds/dot-20wpm.ogg"])
    sleep(ts)

def dah():
    subprocess.call(["paplay", "learnMorse/sounds/dash-20wpm.ogg"])
    sleep(ts)

def charSpace():
    sleep(tc)

def wordSpace():
    sleep(tw)

play = {
    Symbol.DIT: dit,
    Symbol.DAH: dah,
    }

chars = []
for x in range(NUM_CHARS):
    chars.append(morse.popitem(0))

def startTest():
    while running:
        wordLength = random.choice(range(10)) + 1
        for x in range(wordLength):
            char = random.choice(chars)
            for symbol in char[1]:
                play[symbol]()
            charSpace()
        wordSpace()

def stopTest():
    global running
    running = False

def run():
    global running
    running = True
    timer = Timer(300, stopTest)
    timer.start()
    startTest()
