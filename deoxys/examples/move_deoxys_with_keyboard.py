# Script to control the franka with the keyboard
# It will move to each position 

# from abc import ABC, abstractmethod

# import numpy as np
import pygame
import time
import numpy as np
# import time

# from abc import ABC
# from multiprocessing import Process
# from pyPS4Controller.controller import Controller

# from holobot.utils.timer import FrequencyTimer

class FrequencyTimer(object):
    def __init__(self, frequency_rate):
        self.time_available = 1e9 / frequency_rate

    def start_loop(self):
        self.start_time = time.time_ns()

    def end_loop(self):
        wait_time = self.time_available + self.start_time
        
        while time.time_ns() < wait_time:
            continue

class JoystickController():
    def __init__(self):
        pygame.init()
        self.joy = pygame.joystick.Joystick(0)
        self.name = self.joy.get_name()
        self.joy.init()

        self.back_1_buttons = [0, 0] # L1, R1 buttons
        self.back_2_buttons = [0, 0] # L2, R2 button values
        self.l3_values = [0, 0] # x, y values
        self.r3_values = [0, 0] # x, y values
        self.right_buttons =  { # To indicate if they are pressed or not
            'triangle': 0, 
            'circle': 0, 
            'x': 0, 
            'square': 0
        }
        self.left_buttons = { # To indicate if they are pressed or not
            'up': 0, 
            'right': 0, 
            'down': 0, 
            'left': 0
        }

    def detect_event(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.JOYAXISMOTION:
                if event.axis == 0: # L3 - X
                    if event.value > 0.1 or event.value < -0.1:
                        self.l3_values[0] = event.value
                    else:
                        self.l3_values[0] = 0
                    continue
                if event.axis == 1: # L3 - Y
                    if event.value > 0.1 or event.value < -0.1:
                        self.l3_values[1] = event.value
                    else: 
                        self.l3_values[1] = 0
                    continue
                if event.axis == 3: # R3 - X
                    if event.value > 0.1 or event.value < -0.1: 
                        self.r3_values[0] = event.value 
                    else: 
                        self.r3_values[0] = 0
                    continue 
                if event.axis == 4: # R3 - Y 
                    if event.value > 0.1 or event.value < -0.1:
                        self.r3_values[1] = event.value
                    else:
                        self.r3_values[1] = 0
                    continue

            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                    self.right_buttons['x'] = 1
                    continue
                if event.button == 1:
                    self.right_buttons['circle'] = 1
                    continue 
                if event.button == 2:
                    self.right_buttons['triangle'] = 1 
                    continue 
                if event.button == 3:
                    self.right_buttons['square'] = 1
                    continue
                if event.button == 4: # L1
                    self.back_1_buttons[0] = 1
                    continue 
                if event.button == 5: # R1 
                    self.back_1_buttons[1] = 1
                    continue 
                if event.button == 6: # L2 
                    self.back_2_buttons[0] = 1 
                    continue 
                if event.button == 7: # R2
                    self.back_2_buttons[1] = 1
                    continue

            if event.type == pygame.JOYBUTTONUP:
                self.right_buttons[event.button] = False
                if event.button == 0:
                    self.right_buttons['x'] = 0
                    continue
                if event.button == 1:
                    self.right_buttons['circle'] = 0
                    continue 
                if event.button == 2:
                    self.right_buttons['triangle'] = 0
                    continue 
                if event.button == 3:
                    self.right_buttons['square'] = 0
                    continue
                if event.button == 4: # L1
                    self.back_1_buttons[0] = 0
                    continue 
                if event.button == 5: # R1 
                    self.back_1_buttons[1] = 0
                    continue 
                if event.button == 6: # L2 
                    self.back_2_buttons[0] = 0
                    continue 
                if event.button == 7: # R2
                    self.back_2_buttons[1] = 0
                    continue

            if event.type == pygame.JOYHATMOTION:
                if event.value[1] >= 0:
                    self.left_buttons['up'] = event.value[1]
                if event.value[1] <= 0: 
                    self.left_buttons['down'] = -event.value[1]
                if event.value[0] >= 0: 
                    self.left_buttons['right'] = event.value[0]
                if event.value[0] <= 0:
                    self.left_buttons['left'] = -event.value[0]


class VelocityKeyboardController():
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((1,1))

        self.translation = [0,0,0] # End effector position
        self.rotation = [0,0,0] # By euclidean for now 

    def detect_event(self):
        events = pygame.event.get()
        print('events: {}'.format(events))
        for event in events:
            print('event: {}'.format(event))
            if event.type == pygame.KEYDOWN: 
                # print(event.key)
                if event.key == pygame.K_UP:
                    self.translation[0] += 0.1
                if event.key == pygame.K_DOWN:
                    self.translation[0] -= 0.1
                if event.key == pygame.K_LEFT:
                    self.translation[1] += 0.1
                if event.key == pygame.K_RIGHT:
                    self.translation[1] -= 0.1
                if event.key == pygame.K_w:
                    self.translation[2] += 0.1
                if event.key == pygame.K_s:
                    self.translation[2] -= 0.1


class Joystick():
    def __init__(self):
        self._controller = JoystickController()
        self.notify_component_start('Joystick component started!')
        self.timer = FrequencyTimer(15)

    def stream(self):

        while True: 
            try:
                self.timer.start_loop()
                
                joystick_state = self.get_joystick_state()
                print('Joystick State: {}'.format(joystick_state))

                self.timer.end_loop()

            except KeyboardInterrupt:
                break 

    def get_joystick_state(self):
        self._controller.detect_event()
        timestamp = time.time()
        joystick_state = dict(
            right_buttons = np.asarray([
                self._controller.right_buttons['x'], # Starts from x and goes clockwise
                self._controller.right_buttons['square'],
                self._controller.right_buttons['triangle'],
                self._controller.right_buttons['circle']
            ]),
            left_buttons = np.asarray([
                self._controller.left_buttons['down'], # Starts from down and goes clockwise
                self._controller.left_buttons['left'],
                self._controller.left_buttons['up'],
                self._controller.left_buttons['right']
            ]),
            back_buttons = np.asarray(self._controller.back_1_buttons + self._controller.back_2_buttons),
            axes_motions = np.asarray(self._controller.l3_values + self._controller.r3_values), # First two values for l3, last two values for r3
            timestamp = timestamp
        )

        return joystick_state

if __name__ == '__main__':

    # timer = FrequencyTimer(5)
    # joy = Joystick()
    # while True:
    #     try:
    #         timer.start_loop()
    #         joystick_state = joy.get_joystick_state()
    #         print('Joystick State: {}'.format(joystick_state))
    #         timer.end_loop()

    #     except KeyboardInterrupt:
    #         break

    import pygame

    pygame.init()
    pygame.joystick.init()
    pygame.display.init()
    pygame.display.set_mode((640, 480))

    clock = pygame.time.Clock()
    js = pygame.joystick.Joystick(0)
    js.init()

    running = True

    while running:
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            break

        if event.type == pygame.JOYHATMOTION:
            print('FLIP!')
            pygame.display.flip()

        clock.tick(30)

    pygame.quit()


# NOTE: This doesn't work for now - will look into it later!
