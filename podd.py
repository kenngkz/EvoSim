'''

'''

import numpy as np
import random

from settings import PoddSettings as PS, BrainSettings as BS

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

    def __init__(self, genome, id):
        self.id = id
        self.genome = genome
        self._parse_genome()
        self.energy = PS.init_energy
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
                if random.random() < PS.mut_rate:
                    new[attr] *= random.normalvariate(1, PS.mut_var)
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

    def __init__(self, brain_genome):
        self.genome = brain_genome
        self.computations = {}
        self.input_nodes = [f"i{i:04}" for i in range(BS.n_inputs)]
        self.output_nodes = [f"o{i:04}" for i in range(BS.n_outputs)]
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
            self.computations["i" + str(i).zfill(len(str(BS.max_node)))] = val
        output = np.array([self.nodelist[node_id].compute() for node_id in self.output_nodes])
        self.computations = {}
        return output

    def new_node_id(self):
        if len(self.nodelist) >= BS.max_node:
            raise Exception(f"Too many nodes. nodelist too close to maximum capacity: {len(self.nodelist)}/{BS.max_node}")
        while True:
            i = str(random.choice(range(BS.max_node+1))).zfill(len(str(BS.max_node)))
            if i not in self.nodelist:
                return i

    def new_genome(self):
        new = {}
        for connection, weight in self.genome.items():
            if random.random() > BS.chance_del:  # if not deleting
                new[connection] = weight * random.normalvariate(1, BS.mut_var) if abs(weight) > BS.min_mut_weight else weight + BS.min_mut_weight * random.normalvariate(0, BS.mut_var)
        # new connections
        if random.random() < BS.chance_new:
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