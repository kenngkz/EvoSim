'''

'''

import numpy as np
import random

'''
obs: 32 vision inputs, ? internal inputs
actions: turn left, turn right, move forward, move backward --> applied simultaneously
'''

# TODO: what does the genome look like?
'''
start with dict as genome?
genome: {
    "size": , "strength", "vision_spacing", "vision_field", "brain":["i1-o1":10, "i2-o1":-10]
}

attributes: size, strength
brain: map inputs to 3 actions: forward, left, right
'''


class Podd:

    INIT_ENERGY = 100
    FOOD_ENERGY = 10
    ENERGY_CONSUMPTION_MOVING = 1  # energy consumed per second to move
    ENERGY_CONSUMPTION_IDLE = 0.1  # energy consumed per second while idle

    def __init__(self, genome):
        self.genome = genome
        self._parse_genome()
        self.previous_action = np.zeros(3, dtype=np.float32)
        self.energy = self.INIT_ENERGY

    def _parse_genome(self):
        self.attr = {"size":self.genome["size"], "strength":self.genome["strength"]}
        self.brain = None
        
    def choose_action(self, obs):
        self.previous_action += np.array([(random.random()-0.5)/10 for _ in range(3)])
        return [i>0 for i in self.previous_action]