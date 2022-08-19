'''

'''
import random
import Box2D as b2d
from datetime import datetime
from math import sqrt

from custom_framework import CustomFramework as Framework, main
from podd import Podd, generate_brain_genomes
from settings import FrameworkSettings as FS, WorldSettings as WS, PoddSettings as PS
from utils import get_logger

logger = get_logger(__name__)

# constants
MOVEDIR_FRONT = "forward"
MOVEDIR_LEFT = "counter-clockwise"
MOVEDIR_RIGHT = "clockwise"
MOVEDIRS = [MOVEDIR_FRONT, MOVEDIR_LEFT, MOVEDIR_RIGHT]
SEP = ";"  # delimiter for csv

sample_brains = generate_brain_genomes(WS.init_podds)
test_genomes = []
for _ in range(WS.init_podds):
    # test_genomes.append({"size":1, "strength":1, "birth_energy":120, "brain":random.choice(sample_brains)})
    test_genomes.append({"size":1, "strength":1, "birth_energy":50, "brain":{}})

class SimWorld(Framework):
    name = "Simulation world"
    description = "Scroll/Z/X to zoom, Arrow keys to move screen, Esc to quit."

    # timer
    frame_counter = 0

    def __init__(self):
        logger.info(f"WORLD | Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        super(SimWorld, self).__init__()
        self.world.gravity = (0, 0)

        # food
        self.spawn_food_counter = 0
        self.food = set()
        for _ in range(WS.init_food):
            self.add_food()
            self.add_food()

        self.podds = {}  # {id : (fixture, Podd)}
        self.next_id = 1  # podd id increments

        if WS.enable_border:
            c = WS.spawn_food_box/WS.grid
            if not WS.rounded_corners:
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
            f.write(f"id{SEP}parent{SEP}genome\n")

        # test
        for genome in test_genomes:
            # self.add_podd(genome, position=(random.randint(-WS.spawn_food_box, WS.spawn_food_box)/10, random.randint(-WS.spawn_food_box, WS.spawn_food_box)/10))
            self.add_podd(genome, position=(0, 0))
    
    def Step(self, settings):
        self.frame_counter += 1
        # food spawn and display
        self.spawn_food_counter += 1
        if self.spawn_food_counter >= WS.spawn_food_interval and len(self.food) < WS.max_food:
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
                obj[1].energy += WS.food_energy

        # podd movements
        for fixture, podd in self.podds.values():
            move_actions = podd.step([], len(self.podds))
            for i, move in enumerate(move_actions):
                if move:
                    self.move_obj(fixture, MOVEDIRS[i], podd.attr["strength"])
        
        # kill dead podds and birth new podds
        for dead_podd in [podd for fixture, podd in self.podds.values() if podd.dead]:
            self.kill_podd(dead_podd.id)
        for parent_podd in [podd for fixture, podd in self.podds.values() if podd.give_birth]:
            self.birth_podd(parent_podd.id)

        # update stats
        if self.frame_counter % (10*FS.hz) == 0:  # every 10s
            self.update_stats()

    def add_food(self, p=None):
        if p:
            self.food.add(p)
        else:
            self.food.add((random.randint(-WS.spawn_food_box, WS.spawn_food_box)/10, random.randint(-WS.spawn_food_box, WS.spawn_food_box)/10))

    def is_touching_food(self, id, fixture):
        transform = b2d.b2Transform()
        transform.angle = fixture.body.angle
        transform.position = fixture.body.position
        hits = []
        for p in self.food:
            hit = fixture.shape.TestPoint(transform, p)
            if hit:
                logger.debug(f"WORLD | Food hit detected: {id} - {p}")
                hits.append(p)
        return hits

    def display_food(self):
        for p in self.food:
            self.renderer.DrawSolidCircle(self.renderer.to_screen(p), 0.25, (0, 0), b2d.b2Color((0, 1.0, 0)))

    def add_podd(self, genome, position=(0, 0), parent=None):
        scale = sqrt(genome["size"])
        print(scale)
        shape = b2d.b2PolygonShape(vertices=[(0, 0), (-scale, -scale), (scale, -scale)])
        body = self.world.CreateDynamicBody(position=position, angle=random.random()*6.28, angularDamping=5, linearDamping=0.1)
        main_fixture = body.CreateFixture(shape=shape, density=WS.test_density, friction=0.3)
        self.podds[self.next_id] = (main_fixture, Podd(genome, self.next_id, parent))
        self.next_id += 1
        with open(self.censusfile, "a") as f:
            f.write(f"{self.next_id-1}{SEP}{parent}{SEP}{genome}\n")
        return self.next_id - 1

    def kill_podd(self, id):
        # logger.info(f"DEATH : {id} died. Age: {self.podds[id][1].age}. Children: {self.podds[id][1].children}")
        self.world.DestroyBody(self.podds[id][0].body)
        self.podds.pop(id, None)

    def birth_podd(self, id):
        new_podd_genome = self.podds[id][1].new_genome(self.next_id)
        self.podds[id][1].children.append(self.next_id)
        self.add_podd(new_podd_genome, self.podds[id][0].body.position, id)

    def move_obj(self, fixture, movement, strength):
        if movement == MOVEDIR_FRONT:
            fixture.body.ApplyForce(force=fixture.body.GetWorldVector(localVector=(0.0, strength)), point=fixture.body.worldCenter, wake=True)
        if movement == MOVEDIR_LEFT:
            fixture.body.ApplyTorque(WS.turn_scale*strength, wake=True)
        if movement == MOVEDIR_RIGHT:
            fixture.body.ApplyTorque(-WS.turn_scale*strength, wake=True)

    def update_stats(self):
        # history
        time_s = self.frame_counter // FS.hz
        population = len(self.podds)
        if population == 0:
            return
        total_food = len(self.food)
        avg_net_energy = sum([podd[1].energy - podd[1].min_energy for podd in self.podds.values()])/population
        avg_size = sum([podd[1].attr["size"] for podd in self.podds.values()])/population
        avg_strength = sum([podd[1].attr["strength"] for podd in self.podds.values()])/population
        with open(self.statsfile, "a") as f:
            f.write(f"{time_s}{SEP}{population}{SEP}{total_food}{SEP}{avg_net_energy}{SEP}{avg_size}{SEP}{avg_strength}\n")
        logger.info(f"STATS | {time_s=} {population=} {total_food=} {avg_net_energy=}")

if __name__ == "__main__":
    main(SimWorld)