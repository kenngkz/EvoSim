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

class Podd:
    '''
    Represents a Podd: genome, brain, energy etc.
    '''

    INIT_ENERGY = 100
    ENERGY_CONSUMPTION_MOVING = 1  # energy consumed per second to move
    ENERGY_CONSUMPTION_LIVING = 0.5  # energy consumed per second to continue to live

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
        self.previous_action = np.array([0, 0, 0])

    def _parse_genome(self):
        self.attr = {"size":self.genome["size"], "strength":self.genome["strength"]}
        self.birth_energy = self.genome["birth_energy"]
        self.brain = Brain(self.genome["brain"])
        
    def choose_action(self, obs):
        obs = obs + [self.energy, *self.previous_action, random.random()-0.5, 1]
        self.previous_action = self.brain.compute(obs)
        return self.previous_action


    def new_genome(self):  # TODO: revamp this
        new = {}
        for attr, value in self.genome.items():
            if attr == "brain":
                new["brain"] = self.brain.new_genome()
            else:
                new[attr] = value
                if random.random() < self.MUTATION_RATE:
                    new[attr] *= random.normalvariate(1, self.MUTATION_STR)
        return new

### BRAIN ###




## for now just do non-learning neurons
# {node_name-node_name: weight}

def relu(x):
    return x if x>0 else 0
activation = relu

class Node:

    def __init__(self, id, brain, nodelist=None):
        self.id = id
        self.brain = brain
        self.connections = {}  # nodes that feed into this node
        self.nodelist = nodelist if nodelist else {} # list of node ids, shared between all Nodes in a Brain

    def add_connection(self, node_id, weight):
        self.connections[node_id] = (self.nodelist[node_id], weight)

    def compute(self):
        if self.id not in self.brain.computations:
            self.brain.computations[self.id] = activation(sum([node.compute()*weight for node, weight in self.connections.values()]))
        return self.brain.computations[self.id]

class Brain:

    # nodes
    N_INPUTS = 6
    N_OUTPUTS = 3
    MAX_NODE = 9999

    # mutation chance
    CHANCE_NEW = 0.25  # chance at each new_genome of creating a new connection
    CHANCE_DEL = 0.05  # chance of each existing connection of deleting itself
    
    # mutation strength: adjusting weights
    MUT_VAR = 0.1
    MIN_MUT_WEIGHT = 0.01

    def __init__(self, brain_genome):
        self.genome = brain_genome
        self.computations = {}
        self.input_nodes = [f"i{i:04}" for i in range(self.N_INPUTS)]
        self.output_nodes = [f"o{i:04}" for i in range(self.N_OUTPUTS)]
        ionodes = self.input_nodes + self.output_nodes
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
            self.computations["i" + str(i).zfill(len(str(self.MAX_NODE)))] = val
        output = np.array([self.nodelist[node_id].compute() for node_id in self.output_nodes])
        self.computations = {}
        return output

    def new_node_id(self):
        if len(self.nodelist) >= self.MAX_NODE:
            raise Exception(f"Too many nodes. nodelist too close to maximum capacity: {len(self.nodelist)}/{self.MAX_NODE}")
        while True:
            i = str(random.choice(range(self.MAX_NODE+1))).zfill(len(str(self.MAX_NODE)))
            if i not in self.nodelist:
                return i

    def new_genome(self):
        new = {}
        for connection, weight in self.genome.items():
            if random.random() > self.CHANCE_DEL:  # if not deleting
                new[connection] = weight * random.normalvariate(1, self.MUT_VAR) if abs(weight) > self.MIN_MUT_WEIGHT else weight + self.MIN_MUT_WEIGHT * random.normalvariate(0, self.MUT_VAR)
        # new connections
        if random.random() < self.CHANCE_NEW:
            nodes = list(self.nodelist.keys())
            nodes.append(self.new_node_id())
            from_node = random.choice(nodes)
            nodes.remove(from_node)
            new[f"{from_node}-{random.choice(nodes)}"] = random.normalvariate(0, 1)
        return new


def generate_brain_genomes(final_sample, generations=8, n_parents=50, n_children=20):
    brain_genome = {}

    pop = [Brain(brain_genome) for _ in range(n_parents)]
    for _ in range(generations):
        parents = random.sample(pop, 20)
        children = []
        for parent in parents:
            children += [Brain(parent.new_genome()) for _ in range(n_children)]
        pop = children
    return [brain.genome for brain in random.sample(pop, final_sample)]



#### MINIMUM ENERGY THAT INCREASES WITH AGE
# can have podds that dont move continue to recieve energy passively? how to encourage movement? passive energy distributed among podds (and food?)