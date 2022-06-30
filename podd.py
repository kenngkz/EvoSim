'''

'''

import numpy

SMALL = 100

'''
obs: 32 vision inputs, ? internal inputs
actions: turn left, turn right, move forward, move backward --> applied simultaneously
'''

# TODO: what does the genome look like?
'''
mapping for gene value to node, alphanumerical, "." is seperation value
start with dict as genome
genome: {
    "size": , "strength", "vision_spacing", "vision_field", "brain":["i1-o1":10, "i2-o1":-10]
}
'''


class Podd:

    def __init__(self, genome):
        self.brain = None
        

    def take_action(self, obs):
        pass