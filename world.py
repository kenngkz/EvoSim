'''

'''

import Box2D as b2d
import random
import os

from custom_framework import CustomFramework as Framework
from custom_framework import main, Keys
from podd import Podd

MOVEDIR_FRONT = "forward"
MOVEDIR_LEFT = "counter-clockwise"
MOVEDIR_RIGHT = "clockwise"
ENABLE_BORDER = True
ROUNDED_CORNERS = False
SEP = ";"  # delimiter for csv

test_genome = {"size":1, "strength":10, "birth_energy":120, "brain":{"init_prev":[0, 0, 0], "energy":[0, 0, 0], "random_scale":0.1}}

class SimWorld(Framework):
    name = "Simulation world"
    description = "Scroll/Z/X to zoom, Arrow keys to move screen, Esc to quit."

    # food
    SPAWN_FOOD_INTERVAL = 30  # number of frames/steps
    GRID = 10  # smaller -> food spawn further apart
    SPAWN_FOOD_BOX = 60*GRID
    INIT_FOOD = 500
    FOOD_ENERGY = 20  # can be genetically determined in the future

    # timer
    FRAME_COUNTER = 0

    # movement
    TURN_SCALE = 0.5  # ratio of turning force to forward force

    # TEST
    TEST_SCALE = 1  # range [0.5, 2]
    TEST_STR = 7  # range [1, 50]
    TEST_DENSITY = 1

    def __init__(self):
        super(SimWorld, self).__init__()
        self.world.gravity = (0, 0)

        # food
        self.spawn_food_counter = 0
        self.food = set()
        for _ in range(self.INIT_FOOD):
            self.add_food()
            self.add_food()

        self.podds = {}  # {id : (fixture, Podd)}
        self.next_id = 1  # podd id increments

        if ENABLE_BORDER:
            c = self.SPAWN_FOOD_BOX/self.GRID
            if ROUNDED_CORNERS:
                self.border = self.world.CreateStaticBody(
                    shapes=[
                        b2d.b2EdgeShape(vertices=[(c , c), (-c, c)]), b2d.b2EdgeShape(vertices=[(-c, c), (-c, -c)]), b2d.b2EdgeShape(vertices=[(-c, -c), (c, -c)]), b2d.b2EdgeShape(vertices=[(c, -c), (c, c)]),
                    ])
            else:
                self.border = self.world.CreateStaticBody(
                    shapes = [
                        b2d.b2EdgeShape(vertices=[(c-1, c), (-c+1, c)]), b2d.b2EdgeShape(vertices=[(-c+1, c), (-c, c-1)]),
                        b2d.b2EdgeShape(vertices=[(-c, c-1), (-c, -c+1)]), b2d.b2EdgeShape(vertices=[(-c, -c+1), (-c+1, -c)]),
                        b2d.b2EdgeShape(vertices=[(-c+1, -c), (c-1, -c)]), b2d.b2EdgeShape(vertices=[(c-1, -c), (c, -c+1)]),
                        b2d.b2EdgeShape(vertices=[(c, -c+1), (c, c-1)]), b2d.b2EdgeShape(vertices=[(c, c-1), (c-1, c)]),
                    ])

        # statistics
        self.statsfile = "history.csv"
        with open(self.statsfile, "w") as f:
            f.write(f"time{SEP}population{SEP}total_food{SEP}avg_energy{SEP}avg_size{SEP}avg_strength\n")
        self.censusfile = "census.csv"
        with open(self.censusfile, "w") as f:
            f.write(f"id{SEP}parent{SEP}genome")

        # test
        for i in range(15):
            self.add_podd(test_genome)
    
    def Step(self, settings):
        self.FRAME_COUNTER += 1
        # food spawn and display
        self.spawn_food_counter += 1
        if self.spawn_food_counter == self.SPAWN_FOOD_INTERVAL:
            self.spawn_food_counter = 0
            self.add_food()
        self.display_food()

        # run physics
        super(SimWorld, self).Step(settings)

        # check for food overlay
        for id, obj in self.podds.items():
            hits = self.is_touching_food(id, obj[0])
            for hit in hits:
                self.food.remove(hit)
                obj[1].energy += self.FOOD_ENERGY

        # podd movements + energy tracking
        dead_podds = []
        parent_podds = []
        for fixture, podd in self.podds.values():
            move_actions = podd.choose_action(None)
            for direction, applyforce in zip([MOVEDIR_FRONT, MOVEDIR_LEFT, MOVEDIR_RIGHT], move_actions):
                if applyforce:
                    self.move_obj(fixture, direction, podd.attr["strength"])
                    podd.energy -= podd.ENERGY_CONSUMPTION_MOVING/60  # consume energy to move
            podd.energy -= podd.ENERGY_CONSUMPTION_LIVING/60
            podd.age += 1/60  # +1 per second alive
            if podd.energy <= 0:
                dead_podds.append(podd.id)
            if podd.energy >= podd.birth_energy and podd.age >= podd.BIRTH_AGE:
                parent_podds.append(podd.id)
                podd.energy -= podd.BIRTH_COST

        # kill dead podds
        for podd_id in dead_podds:
            self.kill_podd(podd_id)
        # birth new podds
        for podd_id in parent_podds:
            self.birth_podd(podd_id)

        # update stats
        if self.FRAME_COUNTER % 600 == 0:  # every 10s
            self.update_stats()

    def add_food(self, p=None):
        if p:
            self.food.add(p)
        else:
            self.food.add((random.randint(-self.SPAWN_FOOD_BOX, self.SPAWN_FOOD_BOX)/10, random.randint(-self.SPAWN_FOOD_BOX, self.SPAWN_FOOD_BOX)/10))

    def is_touching_food(self, id, fixture):
        transform = b2d.b2Transform()
        transform.angle = fixture.body.angle
        transform.position = fixture.body.position
        hits = []
        for p in self.food:
            hit = fixture.shape.TestPoint(transform, p)
            if hit:
                print(f"Hit: {id} - {p}")
                hits.append(p)
        return hits

    def display_food(self):
        for p in self.food:
            self.renderer.DrawSolidCircle(self.renderer.to_screen(p), 0.25, (0, 0), b2d.b2Color((0, 1.0, 0)))

    def add_podd(self, genome, position=(0, 0), parent=None):
        scale = genome["size"]
        shape = b2d.b2PolygonShape(vertices=[(0, 0), (-scale, -scale), (scale, -scale)])
        body = self.world.CreateDynamicBody(position=position, angularDamping=5, linearDamping=0.1)
        main_fixture = body.CreateFixture(shape=shape, density=self.TEST_DENSITY, friction=0.3)
        self.podds[self.next_id] = (main_fixture, Podd(genome, self.next_id))
        self.next_id += 1
        with open(self.censusfile, "a") as f:
            f.write(f"{self.next_id-1}{SEP}{parent}{SEP}{genome}\n")

    def kill_podd(self, id):
        self.world.DestroyBody(self.podds[id][0].body)
        self.podds.pop(id, None)
        print(f"Podd {id} killed")

    def birth_podd(self, id):
        new_podd_genome = self.podds[id][1].new_genome()
        self.add_podd(new_podd_genome, self.podds[id][0].body.position, id)
        print(f"New podd {self.next_id - 1} born from parent {id}")

    def move_obj(self, fixture, movement, strength):
        if movement == MOVEDIR_FRONT:
            fixture.body.ApplyForce(force=fixture.body.GetWorldVector(localVector=(0.0, strength)), point=fixture.body.worldCenter, wake=True)
        if movement == MOVEDIR_LEFT:
            fixture.body.ApplyTorque(self.TURN_SCALE*strength, wake=True)
        if movement == MOVEDIR_RIGHT:
            fixture.body.ApplyTorque(-self.TURN_SCALE*strength, wake=True)

    def update_stats(self):
        # history
        time_s = self.FRAME_COUNTER // 600
        population = len(self.podds)
        if population == 0:
            return
        total_food = len(self.food)
        avg_energy = sum([podd[1].energy for podd in self.podds.values()])/population
        avg_size = sum([podd[1].attr["size"] for podd in self.podds.values()])/population
        avg_strength = sum([podd[1].attr["strength"] for podd in self.podds.values()])/population
        with open(self.statsfile, "a") as f:
            f.write(f"{time_s}{SEP}{population}{SEP}{total_food}{SEP}{avg_energy}{SEP}{avg_size}{SEP}{avg_strength}\n")

if __name__ == "__main__":
    main(SimWorld)