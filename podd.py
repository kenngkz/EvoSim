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
    "brain":{
        "init_prev":[x, x, x],
        "energy":[x, x, x],
        "random_scale":
    }
}

attributes: size, strength
brain: map inputs to 3 actions: forward, left, right
'''

GENOME_RANGE = {"size":[0.25, 3], "strength":[1, 50]}

class Podd:
    '''
    Represents a Podd: genome, brain, energy etc.
    '''

    INIT_ENERGY = 100
    ENERGY_CONSUMPTION_MOVING = 1  # energy consumed per second to move
    ENERGY_CONSUMPTION_LIVING = 0.1  # energy consumed per second to continue to live

    BIRTH_COST = 100
    BIRTH_AGE = 20  # in seconds

    MUTATION_RATE = 0.5
    MUTATION_STR = 0.1

    def __init__(self, genome, id):
        self.id = id
        self.genome = genome
        self._parse_genome()
        self.energy = self.INIT_ENERGY
        self.age = 0  # number of seconds alive

    def _parse_genome(self):
        self.attr = {"size":self.genome["size"], "strength":self.genome["strength"]}
        self.previous_action = np.array(self.genome["brain"]["init_prev"], dtype=np.float32)
        self.energy_brain = np.array(self.genome["brain"]["energy"], dtype=np.float32)
        self.brain_random_scale = np.array(self.genome["brain"]["random_scale"], dtype=np.float32)
        self.birth_energy = self.genome["birth_energy"]
        self.brain = None
        
    def choose_action(self, obs):
        self.previous_action += np.array([(random.random()-0.5) * self.brain_random_scale for _ in range(3)]) + 0.1 * self.energy * self.energy_brain
        return [i>0 for i in self.previous_action]

    def new_genome(self):
        new = {}
        for attr, value in self.genome.items():
            if attr == "brain":
                new[attr] = {}
                for param, v in value.items():
                    if isinstance(v, list):
                        new[attr][param] = [i + random.normalvariate(1, self.MUTATION_STR*0.1) for i in v]
                    elif isinstance(v, float):
                        new[attr][param] = v + random.normalvariate(1, self.MUTATION_STR)*0.1
                    else:
                        raise Exception(f"Unhandled genome type in brain: {param} - {v}")
            else:
                new_value = value * random.normalvariate(1, self.MUTATION_STR)
                if attr in GENOME_RANGE:
                    if new_value < GENOME_RANGE[attr][0] or new_value > GENOME_RANGE[attr][1] or random.random() < self.MUTATION_RATE:
                        new[attr] = value
                    else:
                        new[attr] = new_value
                else:
                    new[attr] = new_value
        return new

### BRAIN ###

n_inputs = 4  # TODO: trim this section
n_outputs = 3
input_nodes = [f"i{i:04}" for i in range(1, n_inputs+1)]
output_nodes = [f"o{i:04}" for i in range(1, n_outputs+1)]
inputs = [56, 332, 4, 0.2]
max_nodes = 9999

## for now just do non-learning neurons
# {node_name-node_name: weight}
brain_genome = {"i0001-o0001":1, "i0002-o0002":-1, "i0003-o0003":5, "i0004-4253":0.5, "4253-o0001":-0.5}

def relu(x):
    return x if x>0 else 0
activation = relu

class Node:
      # list of node ids, shared between all Nodes

    def __init__(self, id, brain, nodelist=None):
        self.id = id
        self.brain = brain
        self.connections = {}  # nodes that feed into this node
        self.nodelist = nodelist if nodelist else {}

    def add_connection(self, node_id, weight):
        self.connections[node_id] = (self.nodelist[node_id], weight)

    def compute(self):
        if self.id not in self.brain.computations:
            self.brain.computations[self.id] = activation(sum([node.compute()*weight for node, weight in self.connections.values()]))
        return self.brain.computations[self.id]

class Brain:

    def __init__(self, brain_genome):
        self.genome = brain_genome
        self.computations = {}
        ionodes = input_nodes + output_nodes
        self.nodelist = {node_id:Node(node_id, self) for node_id in ionodes}
        for node in self.nodelist.values():
            node.nodelist = self.nodelist
        self.build()

    def build(self):
        for connection, value in self.genome.items():
            nodes = connection.split("-")
            for node_id in nodes: 
                if node_id not in self.nodelist:
                    self.nodelist[node_id] = Node(self.new_node_id(), self, self.nodelist)
            self.nodelist[nodes[1]].add_connection(nodes[0], value)

    def compute(self, input_values):
        for i, val in enumerate(input_values):
            self.computations[f"i{i:04}"] = val
        output = [self.nodelist[node_id].compute() for node_id in output_nodes]
        self.computations = {}
        return output

    def new_node_id(self):
        if len(self.nodelist) >= max_nodes:
            raise Exception(f"Too many nodes. nodelist too close to maximum capacity: {len(self.nodelist)}/{max_nodes}")
        while True:
            i = str(random.choice(range(max_nodes+1)))
            if i not in self.nodelist:
                return i

test = Brain(brain_genome)