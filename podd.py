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
    "size",        [0.5  2]
    "strength",        [1  50]
    "vision_spacing", 
    "vision_field", 
    "brain":["i1-o1":10, "i2-o1":-10]
}

attributes: size, strength
brain: map inputs to 3 actions: forward, left, right
'''

GENOME_RANGE = {"size":[0.5, 2], "strength":[1, 50]}

class Podd:
    '''
    Represents a Podd: genome, brain, energy etc.
    '''

    INIT_ENERGY = 100
    ENERGY_CONSUMPTION_MOVING = 1  # energy consumed per second to move
    ENERGY_CONSUMPTION_LIVING = 0.1  # energy consumed per second to continue to live

    MUTATION_RATE = 0.5
    MUTATION_STR = 0.1

    def __init__(self, genome, id):
        self.id = id
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

    def new_genome(self):
        new = {}
        for attr, value in self.genome.items():
            if random.random() > self.MUTATION_RATE:
                new_value = value + random.normalvariate(0, self.MUTATION_STR)
                if new_value < GENOME_RANGE[attr][0] or new_value > GENOME_RANGE[attr][1]:
                    new[attr] = value
                else:
                    new[attr] = new_value
        return new