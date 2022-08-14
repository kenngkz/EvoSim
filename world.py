'''

'''

import Box2D as b2d
import random
import os
import logging

from custom_framework import CustomFramework as Framework
from custom_framework import main, fwSettings
from podd import Podd, generate_brain_genomes

MOVEDIR_FRONT = "forward"
MOVEDIR_LEFT = "counter-clockwise"
MOVEDIR_RIGHT = "clockwise"
ENABLE_BORDER = True
ROUNDED_CORNERS = False
SEP = ";"  # delimiter for csv

fwSettings.hz = 30
n_podds_init = 100
sample_brains = generate_brain_genomes(100)
test_genomes = []
for _ in range(n_podds_init):
    test_genomes.append({"size":1, "strength":1, "birth_energy":120, "brain":random.choice(sample_brains)})

class SimWorld(Framework):
    name = "Simulation world"
    description = "Scroll/Z/X to zoom, Arrow keys to move screen, Esc to quit."

    # food
    SPAWN_FOOD_INTERVAL = 0.5 * fwSettings.hz  # number of frames/steps
    GRID = 10  # smaller -> food spawn further apart
    SPAWN_FOOD_BOX = 60 * GRID
    INIT_FOOD = 500
    FOOD_ENERGY = 20  # can be genetically determined in the future

    # timer
    FRAME_COUNTER = 0

    # movement
    TURN_SCALE = 0.5  # ratio of turning force to forward force

    # TEST
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
            if not ROUNDED_CORNERS:
                self.border = self.world.CreateStaticBody(
                    fixtures = [
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(c , c), (-c, c)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(-c, c), (-c, -c)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(-c, -c), (c, -c)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(c, -c), (c, c)]), friction=0)
                        ])
            else:
                self.border = self.world.CreateStaticBody(
                    fixtures = [
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(c-1, c), (-c+1, c)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(-c+1, c), (-c, c-1)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(-c, c-1), (-c, -c+1)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(-c, -c+1), (-c+1, -c)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(-c+1, -c), (c-1, -c)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(c-1, -c), (c, -c+1)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(c, -c+1), (c, c-1)]), friction=0),
                        b2d.b2FixtureDef(shape=b2d.b2EdgeShape(vertices=[(c, c-1), (c-1, c)]), friction=0),
                    ])

        # statistics
        self.statsfile = "history.csv"
        with open(self.statsfile, "w") as f:
            f.write(f"time{SEP}population{SEP}total_food{SEP}avg_energy{SEP}avg_size{SEP}avg_strength\n")
        self.censusfile = "census.csv"
        with open(self.censusfile, "w") as f:
            f.write(f"id{SEP}parent{SEP}genome")

        # test
        for genome in test_genomes:
            self.add_podd(genome, position=(random.randint(-self.SPAWN_FOOD_BOX, self.SPAWN_FOOD_BOX)/10, random.randint(-self.SPAWN_FOOD_BOX, self.SPAWN_FOOD_BOX)/10))
    
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
            move_actions = podd.choose_action([])
            for direction, applyforce in zip([MOVEDIR_FRONT, MOVEDIR_LEFT, MOVEDIR_RIGHT], move_actions):
                if applyforce:
                    self.move_obj(fixture, direction, podd.attr["strength"])
                    podd.energy -= podd.ENERGY_CONSUMPTION_MOVING/fwSettings.hz  # consume energy to move
            podd.energy -= podd.ENERGY_CONSUMPTION_LIVING/fwSettings.hz
            podd.age += 1/fwSettings.hz  # +1 per second alive
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
                logging.debug(f"Food hit detected: {id} - {p}")
                hits.append(p)
        return hits

    def display_food(self):
        for p in self.food:
            self.renderer.DrawSolidCircle(self.renderer.to_screen(p), 0.25, (0, 0), b2d.b2Color((0, 1.0, 0)))

    def add_podd(self, genome, position=(0, 0), parent=None):
        scale = genome["size"]
        shape = b2d.b2PolygonShape(vertices=[(0, 0), (-scale, -scale), (scale, -scale)])
        body = self.world.CreateDynamicBody(position=position, angle=random.random()*6.28, angularDamping=5, linearDamping=0.1)
        main_fixture = body.CreateFixture(shape=shape, density=self.TEST_DENSITY, friction=0.3)
        self.podds[self.next_id] = (main_fixture, Podd(genome, self.next_id))
        self.next_id += 1
        with open(self.censusfile, "a") as f:
            f.write(f"{self.next_id-1}{SEP}{parent}{SEP}{genome}\n")

    def kill_podd(self, id):
        self.world.DestroyBody(self.podds[id][0].body)
        self.podds.pop(id, None)
        logging.info(f"Podd {id} died")

    def birth_podd(self, id):
        new_podd_genome = self.podds[id][1].new_genome()
        self.add_podd(new_podd_genome, self.podds[id][0].body.position, id)
        logging.info(f"New podd {self.next_id - 1} born from parent {id}. Genome: {new_podd_genome}")

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
        logging.info(f"Stats : {time_s} {SEP} {population} {SEP} {total_food} {SEP} {avg_energy} {SEP} {avg_size} {SEP} {avg_strength}")

if __name__ == "__main__":
    main(SimWorld)