#!/usr/bin/env python3

import os, sys, logging
import robomodules as rm
from random import randint
from messages import *
# from pacbot.variables import game_frequency, ticks_per_update, pacbot_starting_pos
from pacbot.variables import *
from pacbot.grid import *
from pacbot import StateConverter, GameState
import subprocess
from threading import Thread
import time
import tensorflow as tf
ADDRESS = os.environ.get("BIND_ADDRESS","localhost")
PORT = os.environ.get("BIND_PORT", 11297)

FREQUENCY = game_frequency * ticks_per_update


class GameEngine(rm.ProtoModule):
    def __init__(self, addr, port):
        self.subscriptions = [MsgType.PACMAN_LOCATION, MsgType.FULL_STATE, MsgType.LIGHT_STATE]
        super().__init__(addr, port, message_buffers, MsgType, FREQUENCY, self.subscriptions)
        self.loop.add_reader(sys.stdin, self.keypress)
        self.game = GameState()
        self.pacbot_pos = [pacbot_starting_pos[0], pacbot_starting_pos[1]]
        self.cur_dir = right
        self.next_dir = right
        self.state = PacmanState()
        self.state.mode = PacmanState.PAUSED
        self.lives = starting_lives
        self.clicks = 0
        self.light_state = StateConverter.convert_game_state_to_light(self.game)
        # self.J = 0
        # InputModule.main()
        # self.loop.run_until_complete(self.runsim())
        # self.tf = asyncio.new_event_loop()
        # self.tf.run_forever(self.hello())


    def _write_state(self):
        full_state = StateConverter.convert_game_state_to_full(self.game)
        self.write(full_state.SerializeToString(), MsgType.FULL_STATE)

        light_state = StateConverter.convert_game_state_to_light(self.game)
        self.write(light_state.SerializeToString(), MsgType.LIGHT_STATE)
        self.light_state = light_state
        # if (self.game.play):
        #         logging.info('Game is paused')
        #         self.game.pause()
        #     else:
        #         logging.info('Game resumed')
        #         self.game.unpause()
    def msg_received(self, msg, msg_type):
        if msg_type == MsgType.PACMAN_LOCATION:
            self.game.pacbot.update((msg.x, msg.y))
        if msg_type == MsgType.FULL_STATE:
            self.state = msg
            if self.state.lives != self.lives:
                self.lives = self.state.lives
                self.pacbot_pos = [pacbot_starting_pos[0], pacbot_starting_pos[1]]

    def _move_if_valid_dir(self, direction, x, y):
        if direction == right and grid[x + 1][y] not in [I, n]:
            self.pacbot_pos[0] += 1
            self.cur_dir = direction
            return True
        elif direction == left and grid[x - 1][y] not in [I, n]:
            self.pacbot_pos[0] -= 1
            self.cur_dir = direction
            return True
        elif direction == up and grid[x][y + 1] not in [I, n]:
            self.pacbot_pos[1] += 1
            self.cur_dir = direction
            return True
        elif direction == down and grid[x][y - 1] not in [I, n]:
            self.pacbot_pos[1] -= 1
            self.cur_dir = direction
            return True
        return False

    def tick(self):
        # this function will get called in a loop with FREQUENCY frequency
        # print(self.game.play)
        #gotta set speed
        if self.game.play == False:
            if self.game.endofgame == False:
                self.game.unpause()
            else:
                self.game.restart()
                self.game.endofgame = False
                self.game.unpause()


        if self.game.play:
            # update_pacbot_pos
            if not self._move_if_valid_dir(self.next_dir, self.pacbot_pos[0], self.pacbot_pos[1]):
                self._move_if_valid_dir(self.cur_dir, self.pacbot_pos[0], self.pacbot_pos[1])
            pos_buf = PacmanState.AgentState()
            pos_buf.x = self.pacbot_pos[0]
            pos_buf.y = self.pacbot_pos[1]
            pos_buf.direction = self.cur_dir
            self.write(pos_buf.SerializeToString(), MsgType.PACMAN_LOCATION)
            self.next_dir = randint(0,3)
            # print(self.light_state.score)
            # for i in range(0,10000000):
            #     x = i*100
            # print(self.J)
            # self.J+= 1
            # self.state.mode = PacmanState.PAUSED;

            # This will become asynchronous
            self.game.next_step()
        self._write_state()

    def runsim(self):
        print("hello")
        timesteps = 10
        logging.info("Restarsting...")
        self.game.restart()
        self._write_state()
        if (self.game.play):
            logging.info('Game is paused')
            self.game.pause()
        else:
            logging.info('Game resumed')
            self.game.unpause()
        for i in range(0, timesteps):
            # self.game.unpause()
            while True:
                pass
    def packey(self):
        char = sys.stdin.read(1)
        if char == 'a':
            self.next_dir = left
        elif char == 'd':
            self.next_dir = right
        elif char == 'w':
            self.next_dir = up
        elif char == 's':
            self.next_dir = down
        elif char == 'q':
            self.quit()
    def keypress(self):
        char = sys.stdin.read(1)
        # For some reason I couldn't quite get this to do what I wanted
        # Still it's a bit cleaner than otherwise
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        sys.stdout.flush()
        if char == "r":
            logging.info("Restarting...")
            self.game.restart()
            self._write_state()
        elif char == "p":
            if (self.game.play):
                logging.info('Game is paused')
                self.game.pause()
            else:
                logging.info('Game resumed')
                self.game.unpause()
        elif char == "q":
            logging.info("Quitting...")
            self.quit() 

def main():
    # subprocess.Popen("./hello.py")
    # logger automatically adds timestamps
    # I wanted it to print each sequentially but it did not want to
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s',
                        datefmt="%I:%M:%S %p")
    engine = GameEngine(ADDRESS, PORT)
    print('Game is paused.')
    print('Controls:')
    print('    r - restart')
    print('    p - (un)pause')
    print('    q - quit')
    engine.run()
    # T1 = Thread(target=engine.run(), args=())
    # T2 = Thread(target=engine.runsim(), args=())
    # T1.start()
    # T2.start()
    # T2.join()
    # T1.join()

    # engine.run()



if __name__ == "__main__":
    main()
