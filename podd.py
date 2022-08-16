'''

'''

import numpy as np
import random

from settings import PoddSettings as PS, BrainSettings as BS, FrameworkSettings as FS, WorldSettings as WS
from utils import get_logger

logger = get_logger(__name__)

'''
obs: 32 vision inputs, ? internal inputs
actions: turn left, turn right, move forward, move backward --> applied simultaneously
'''

# TODO: what does the genome look like?
'''
start with dict as genome?
genome: {
    "size",
    "strength",
    "brain":{

    }
}

attributes: size, strength
brain: map inputs to 3 actions: forward, left, right
'''

def death_rate(age):
    return PS.fixed_death_rate + age * PS.age_deterioration

death_rates = [death_rate(i) for i in range(240)]  # death rate jump up every second to update to new age


class Podd:
    '''
    Represents a Podd: genome, brain, energy etc.
    '''

    def __init__(self, genome, id, parent=None):
        self.id = id
        self.genome = genome
        self.parent = parent
        self.children = []
        self._parse_genome()
        self.energy = PS.init_energy
        self.min_energy = 0
        self.age = 0  # number of seconds alive
        self.previous_action = np.array([0, 0, 0])

    def _parse_genome(self):
        self.attr = {"size":self.genome["size"], "strength":self.genome["strength"]}
        self.birth_energy = self.genome["birth_energy"]
        self.brain = Brain(self.genome["brain"], self.id)

    def step(self, obs, n_podds):
        # bookkeeping
        self.age += 1/FS.hz
        self.min_energy += PS.age_factor * 2 * (random.random()>0.5)
        self.energy = min(self.energy, PS.max_energy)
        self.dead = False
        self.give_birth = False
        # choose action
        obs = obs + [self.energy, *self.previous_action, random.random()-0.5, 1]
        self.previous_action = self.brain.compute(obs)
        # energy tracking
        self.energy += WS.sunlight_energy / n_podds
        self.energy -= PS.ec_moving * sum([action > 0 for action in self.previous_action])
        self.energy -= PS.ec_living
        # status effects
        if self.energy <= self.min_energy:
            cause = "no_energy"
        elif len(self.previous_action) == 0:
            cause = "brain_malfunction"
        elif random.random() < death_rates[int(self.age)]:
            cause = "age"
        else:
            cause = None
        if cause:
            self.dead = True
            logger.info(f"DEATH : {self.id} died. Cause: {cause} Age: {self.age:02f} Children: {self.children}")
        if self.energy >= self.birth_energy+self.min_energy and self.age >= PS.birth_age:
            self.give_birth = True
            self.energy -= PS.birth_cost
        return [action > 0 for action in self.previous_action]

    def new_genome(self):
        new = {}
        for attr, value in self.genome.items():
            if attr == "brain":
                new["brain"] = self.brain.new_genome()
            else:
                new[attr] = value
                if random.random() < PS.mut_rate:
                    new[attr] *= random.normalvariate(1, PS.mut_sd)
        return new

    def print_genome(self):
        s = ""
        for attr, val in self.genome.items():
            if attr == "brain":
                s += self.brain.print_genome()
            else:
                s += f"{attr}:{val:.04f} "
        return s

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

    def __init__(self, brain_genome, id=None):
        self.id = id
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
        try:
            output = np.array([self.nodelist[node_id].compute() for node_id in self.output_nodes])
        except Exception as e:
            logger.debug(f"Podd {self.id} brain died due to exception: {e}")
            output = []
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
                new[connection] = weight * random.normalvariate(1, BS.mut_sd) if abs(weight) > BS.min_mut_weight else weight + BS.min_mut_weight * random.normalvariate(0, BS.mut_sd)
        # new connections
        if random.random() < BS.chance_new:
            nodes = list(self.nodelist.keys())
            nodes.append(self.new_node_id())
            from_node = random.choice(nodes)
            nodes.remove(from_node)
            new[f"{from_node}-{random.choice(nodes)}"] = random.normalvariate(0, 1)
        return new

    def print_genome(self):
        s = "brain-{"
        for connection, weight in self.genome.items():
            s += f"{connection}:{weight:04f} "
        s += "}"
        return s


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
