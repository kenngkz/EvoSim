import Box2D as b2d
import random

from custom_framework import CustomFramework as Framework
from custom_framework import main, Keys
from podd import Podd

MOVEDIR_FRONT = "forward"
MOVEDIR_LEFT = "counter-clockwise"
MOVEDIR_RIGHT = "clockwise"
ENABLE_BORDER = True

test_genome = {"size":1, "strength":10}

class SimWorld(Framework):
    name = "Simulation world"
    description = "Scroll/Z/X to zoom, Arrow keys to move screen, Esc to quit."

    # food
    SPAWN_FOOD_INTERVAL = 60  # number of frames/steps
    SPAWN_FOOD_BOX = 40*10
    INIT_FOOD = 100

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

        self.podds = {}
        self.next_id = 1

        if ENABLE_BORDER:
            self.border = self.world.CreateStaticBody(
            shapes=[b2d.b2EdgeShape(vertices=[(self.SPAWN_FOOD_BOX/10, self.SPAWN_FOOD_BOX/10), (-self.SPAWN_FOOD_BOX/10, self.SPAWN_FOOD_BOX/10)]),
                    b2d.b2EdgeShape(vertices=[(-self.SPAWN_FOOD_BOX/10, self.SPAWN_FOOD_BOX/10), (-self.SPAWN_FOOD_BOX/10, -self.SPAWN_FOOD_BOX/10)]),
                    b2d.b2EdgeShape(vertices=[(-self.SPAWN_FOOD_BOX/10, -self.SPAWN_FOOD_BOX/10), (self.SPAWN_FOOD_BOX/10, -self.SPAWN_FOOD_BOX/10)]),
                    b2d.b2EdgeShape(vertices=[(self.SPAWN_FOOD_BOX/10, -self.SPAWN_FOOD_BOX/10), (self.SPAWN_FOOD_BOX/10, self.SPAWN_FOOD_BOX/10)]),
                    ])

        # test
        for i in range(10):
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
                obj[1].energy += obj[1].FOOD_ENERGY

        # podd movements
        for fixture, podd in self.podds.values():
            move_actions = podd.choose_action(None)
            for direction, applyforce in zip([MOVEDIR_FRONT, MOVEDIR_LEFT, MOVEDIR_RIGHT], move_actions):
                if applyforce:
                    self.move_obj(fixture, direction, podd.attr["strength"])
                    podd.energy -= podd.ENERGY_CONSUMPTION_MOVING/60  # consume energy to move
            podd.energy -= podd.ENERGY_CONSUMPTION_LIVING

            # TODO: kill podd if no energy left
            if podd.energy <= 0:
                pass

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

    def add_podd(self, genome, position=(0, 0)):
        scale = genome["size"]
        shape = b2d.b2PolygonShape(vertices=[(0, 0), (-scale, -scale), (scale, -scale)])
        body = self.world.CreateDynamicBody(position=position, angularDamping=5, linearDamping=0.1)
        main_fixture = body.CreateFixture(shape=shape, density=self.TEST_DENSITY, friction=0.3)
        self.podds[self.next_id] = (main_fixture, Podd(genome))
        self.next_id += 1

    def move_obj(self, fixture, movement, strength):
        if movement == MOVEDIR_FRONT:
            fixture.body.ApplyForce(force=fixture.body.GetWorldVector(localVector=(0.0, strength)), point=fixture.body.worldCenter, wake=True)
        if movement == MOVEDIR_LEFT:
            fixture.body.ApplyTorque(self.TURN_SCALE*strength, wake=True)
        if movement == MOVEDIR_RIGHT:
            fixture.body.ApplyTorque(-self.TURN_SCALE*strength, wake=True)

    # def Keyboard(self, key):
    #     if len(self.podds) == 0:
    #         return
    #     if key == Keys.K_w:
    #         self.move_obj(self.objects[1][0], MOVEDIR_FRONT, self.TEST_STR)
    #     elif key == Keys.K_a:
    #         self.move_obj(self.objects[1][0], MOVEDIR_LEFT, self.TEST_STR)
    #     elif key == Keys.K_d:
    #         self.move_obj(self.objects[1][0], MOVEDIR_RIGHT, self.TEST_STR)

if __name__ == "__main__":
    main(SimWorld)