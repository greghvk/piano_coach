import pygame, sys
from pygame.locals import*
import random
from utilities import *
import pygame
from mido import MidiFile
import time

pygame.init()
SCREENWIDTH = 1280
SCREENHEIGHT = 780
BLACK = (0, 0, 0)
RED = (255,0,0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
LIGHTGRAY = (217, 217, 217)
DARKGRAY = (191, 191, 191)
bg = pygame.image.load("PIANO.jpeg")
BUTTON_WIDTH = 300
BUTTON_HEIGHT = 90
BUTTON_DOWN = DARKGRAY
BUTTON_UP = LIGHTGRAY
BUTTON_INACTIVE = (230, 230, 230)

class PlayCoach:
    inDevice = None
    def __init__(self):
        pygame.midi.init()
        pygame.mixer.init()
        pygame.mixer.music.load('wrong.wav')
        self.screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        self.menu_font = pygame.font.SysFont('arial', 32) 
        self.game_font = pygame.font.SysFont('arial', 64)
        self.screen_color = WHITE
        self.is_loaded = False
        # print("Choose device:")
        # print_devices()
        # device_idx = input()
        self.inDevice = pygame.midi.Input(0)
        self.config(barsRewinded = 1)
    
    def main_menu(self):
        running = True
        filename = ""
        while running:
            click = False
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                    elif event.key == K_RETURN:
                        self.readSong(filename)
                        filename = ""
                    elif event.key == K_BACKSPACE:
                        filename = filename[:-1]
                    else:
                        filename += event.unicode

            self.screen.fill(WHITE)
            self.screen.blit(bg, [0, SCREENHEIGHT/2])

            mouse_pos = pygame.mouse.get_pos()
           
            b1 = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
            b1_pos = (SCREENWIDTH/2, SCREENHEIGHT/6)
            b1.center = b1_pos
            if self.is_loaded:
                b1_color = BUTTON_UP
                b1_text = "PLAY " + self.song_name
                b1_font_color = BLACK
            else:
                b1_color = BUTTON_INACTIVE
                b1_text = "LOAD SONG TO PLAY"
                b1_font_color = DARKGRAY

            b2 = pygame.Rect(0, 0, BUTTON_WIDTH-100, BUTTON_HEIGHT)
            b2_pos = (SCREENWIDTH/2-50, 2*SCREENHEIGHT/6)
            b2.center = b2_pos
            b2_color = BUTTON_UP
            
            b2_2 = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
            b2_2_pos = (SCREENWIDTH/2+210, 2*SCREENHEIGHT/6)
            b2_2.center = b2_2_pos
            b2_2_color = BUTTON_UP
            
            b3 = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
            b3_pos = (SCREENWIDTH/2, 3*SCREENHEIGHT/6)
            b3.center = b3_pos
            b3_color = BUTTON_UP
            
            if b1.collidepoint(mouse_pos) and self.is_loaded:
                b1_color = BUTTON_DOWN
                if click:
                    self.playSong(self.song)
            if b2.collidepoint(mouse_pos):
                b2_color = BUTTON_DOWN
                if click:
                    self.readSong(filename)
                    filename = ""
            if b3.collidepoint(mouse_pos): 
                b3_color = BUTTON_DOWN
                if click:
                    pygame.quit()
            self.drawButtonWithText(b1, b1_text, b1_color, font_color=b1_font_color) 
            self.drawButtonWithText(b2, "LOAD SONG:", b2_color) 
            self.drawButtonWithText(b2_2, filename, b2_2_color) 
            self.drawButtonWithText(b3, "EXIT", b3_color) 
            pygame.display.update()
    
    def drawButtonWithText(self, button, text, color, width=BUTTON_WIDTH, height=BUTTON_HEIGHT, font_color=BLACK):
            t = self.menu_font.render(text, True, font_color)
            t_obj = t.get_rect()
            t_obj.center = button.center
            pygame.draw.rect(self.screen, color, button)
            self.screen.blit(t, t_obj)
        

    def config(self, barsRewinded = None):
        if barsRewinded != None:
            self.barsRewinded = barsRewinded

    def readSong(self, name):
        try:
            song = MidiFile(name, clip=True)
            left = song.tracks[1]
            right = song.tracks[0]
            left_parsed = parse_to_list(left)
            right_parsed = parse_to_list(right)
            self.song = merge(left_parsed, right_parsed)
            self.song_name = name
            self.is_loaded = True
        except:
            return

    def drawRewindingConfig(self, x, y):
        pygame.draw.polygon(window, BLACK, ((0, 100), (0, 200), (200, 200), (200, 300), (300, 150), (200, 0), (200, 100)))

    
    def addText(self, text, pos, centered=False):
        t1 = self.game_font.render(text, True, BLACK, pos)
        t1_obj = t1.get_rect()
        if centered:
            self.screen.blit(t1, (SCREENWIDTH/2 - 100, pos[1]))
            return
        self.screen.blit(t1, pos)

    def readInput(self):
        while True:
            if self.inDevice.poll():
                event = self.inDevice.read(1)
                print (event)
                if (event[0][0][1] == 21):
                    return
    
    def updateScreenColor(self):
        r = self.screen_color[0]
        g = self.screen_color[1]
        b = self.screen_color[2]
        self.screen_color = (min(255, r+10), min(255, g+10), min(255, b+10))
        
    def playSong(self, song):
        keysDown = set()
        curChord = 0
        pedalCounter = 0
        self.clearPoll()
        text = ""
        while True:
            click = False
            mouse_pos = pygame.mouse.get_pos()
            self.updateScreenColor()
            self.screen.fill(self.screen_color)
            self.screen.blit(bg, [0, SCREENHEIGHT/2])
            curTab = self.song[curChord][2]
            self.addText("Bar: " + str(curTab), (400, 50), True)
            self.addText("Notes in bar: " + str(curChord), (400, 100), True)
            to_play_text = "To play: "+" ".join([translateToNote(x) for x in song[curChord][0]])
            self.addText(to_play_text, (400, 150), True)
            cur_notes_text = " ".join([translateToNote(x) for x in keysDown])
            if not cur_notes_text:
                cur_notes_text = "None"
            played_text = "Currently played: " + cur_notes_text
            self.addText(played_text, (400, 200), True)
            
            bar_butt1 = pygame.Rect(0, 0, BUTTON_WIDTH-100, BUTTON_HEIGHT)
            bar_butt1_pos = (SCREENWIDTH/2-50, 3*SCREENHEIGHT/6)
            bar_butt1.center = bar_butt1_pos
            bar_butt1_color = BUTTON_UP
            
            b2_2 = pygame.Rect(0, 0, BUTTON_WIDTH-250, BUTTON_HEIGHT)
            b2_2_pos = (SCREENWIDTH/2+110, 3*SCREENHEIGHT/6)
            b2_2.center = b2_2_pos
            b2_2_color = BUTTON_UP
            
            back = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
            back_pos = (SCREENWIDTH/2, 4*SCREENHEIGHT/6)
            back.center = back_pos
            back_color = BUTTON_UP

            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        click = True
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                    elif event.key == K_RETURN:
                        try:
                            curChord, curTab = self.jumpToBar(int(text))
                            text = ""
                        except:
                            text = ""
                    elif event.key == K_BACKSPACE:
                        text = text[:-1]
                    elif event.key <= 127:
                        text += event.unicode
            
            if back.collidepoint(mouse_pos): 
                back_color = BUTTON_DOWN
                if click:
                    return
            self.drawButtonWithText(bar_butt1, "JUMP TO BAR:", bar_butt1_color) 
            self.drawButtonWithText(b2_2, text, b2_2_color) 
            self.drawButtonWithText(back, "BACK", back_color) 
            pygame.display.update()
            
            if self.inDevice.poll():
                event = self.inDevice.read(1)
                # Stop song by lowest A
                if (event[0][0][1] == 21):
                    return  
                
                # Jump chord backward
                if (event[0][0][1] == 22) and event[0][0][0] != 128:
                    curChord = max(0, curChord-1)
                    continue  
                
                # Jump chord forward
                if (event[0][0][1] == 23) and event[0][0][0] != 128:
                    curChord = min(len(song), curChord+1)
                    continue  

                # Detect keys up and pass
                if event[0][0][0] == 128:
                    print(f"Key {event[0][0][1]} up")
                    if event[0][0][1] in keysDown:
                        keysDown.remove(event[0][0][1])
                    continue

                # Count pedal presses
                if event[0][0][0] == 176:
                    pedalCounter += 1
                    if pedalCounter == 4:
                        curChord = self.backTabs(curChord)
                        return
                
                # Mistake was made
                if (event[0][0][1]) not in song[curChord][0]:
                    self.screen_color = RED
                    self.screen.fill(self.screen_color)
                    pygame.display.update()
                    pygame.mixer.music.play()
                    print(f"Mistake! played note: {event[0][0][1]}, Needed notes: {song[curChord][0]}")
                    keysDown.add(event[0][0][1])
                    curChord = self.backTabs(curChord)
                    time.sleep(1)
                    self.clearPoll()
                    keysDown = set()
                # Right note
                else:
                    self.screen_color = GREEN
                    print("Right Note!")
                    keysDown.add(event[0][0][1])
                    if (set(song[curChord][0]).issubset(keysDown)):
                        curChord += 1
                        if curChord == len(song):
                            print("Song completed!")
                            return
                        
    def jumpToBar(self, targetBar):
        for chordNum, chord in enumerate(self.song):
            if(chord[2] == targetBar):
                return (chordNum, targetBar)

    def backTabs(self, chordNum):
        curTab = self.song[chordNum][2]
        barToReturn = curTab - self.barsRewinded
        if barToReturn <= 0:
            return 0
        while self.song[chordNum][2] >= barToReturn:
            chordNum -= 1
        return chordNum
            
    def clearPoll(self):
        while self.inDevice.poll():
            self.inDevice.read(1)
    
    def __del__(self):
        pygame.midi.quit()
        pygame.mixer.quit()
        pygame.quit()
