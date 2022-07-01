import Box2D as b2d
import random

from custom_framework import CustomFramework as Framework
from custom_framework import main, Keys

MOVEDIR_FRONT = "forward"
MOVEDIR_LEFT = "counter-clockwise"
MOVEDIR_RIGHT = "clockwise"

class SimWorld(Framework):
    name = "Simulation world"
    description = "Scroll/Z/X to zoom, Arrow keys to move screen, Esc to quit."

    # food
    SPAWN_FOOD_INTERVAL = 60  # number of frames/steps
    SPAWN_FOOD_BOX = 20*10
    INIT_FOOD = 10

    # timer
    FRAME_COUNTER = 0

    # movement
    TURN_SCALE = 0.5  # ratio of turning force to forward force

    # TEST
    TEST_SCALE = 2
    TEST_STR = 50

    def __init__(self):
        super(SimWorld, self).__init__()
        self.world.gravity = (0, 0)

        # food
        self.spawn_food_counter = 0
        self.food = set()
        for _ in range(self.INIT_FOOD):
            self.add_food()

        self.objects = []

        self.add_obj(self.TEST_SCALE, (0, 0), 1)
        print(self.objects[0][1])
    
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
        for obj in self.objects:
            hits = self.is_touching_food(obj[0], obj[1])
            for hit in hits:
                self.food.remove(hit)

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

    def add_obj(self, scale, position, density):  # scale range [0.5, 2]
        shape = b2d.b2PolygonShape(vertices=[(0, 0), (-scale, -scale), (scale, -scale)])
        body = self.world.CreateDynamicBody(position=position, angularDamping=5, linearDamping=0.1)
        fixture = body.CreateFixture(shape=shape, density=density, friction=0.3)
        self.objects.append((random.randint(1, 10000), fixture))

    def move_obj(self, fixture, movement, strength):
        if movement == MOVEDIR_FRONT:
            fixture.body.ApplyForce(force=fixture.body.GetWorldVector(localVector=(0.0, strength)), point=fixture.body.worldCenter, wake=True)
        if movement == MOVEDIR_LEFT:
            fixture.body.ApplyTorque(self.TURN_SCALE*strength, wake=True)
        if movement == MOVEDIR_RIGHT:
            fixture.body.ApplyTorque(-self.TURN_SCALE*strength, wake=True)

    def Keyboard(self, key):
        if len(self.objects) == 0:
            return

        if key == Keys.K_w:
            self.move_obj(self.objects[0][1], MOVEDIR_FRONT, self.TEST_STR)
        elif key == Keys.K_a:
            self.move_obj(self.objects[0][1], MOVEDIR_LEFT, self.TEST_STR)
        elif key == Keys.K_d:
            self.move_obj(self.objects[0][1], MOVEDIR_RIGHT, self.TEST_STR)

if __name__ == "__main__":
    main(SimWorld)