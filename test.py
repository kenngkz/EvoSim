import Box2D as b2d
from Box2D.examples.framework import Framework, main

class Hello(Framework):
    name = "HelloWorld"
    description = "Box falling."

    def __init__(self):
        super(Hello, self).__init__()
        self.world.gravity = (0, -1)
        self.ground = self.world.CreateStaticBody(
            position = (0,-10),
            shapes = b2d.b2PolygonShape(box=(50,10)),
            )
        fixture = b2d.b2FixtureDef(shape=b2d.b2PolygonShape(box=(1, 1)), density=1, friction=0.3)
        self.body = self.world.CreateDynamicBody(position=(0, 10), fixtures=fixture, linearVelocity=(0, 0))

    def Step(self, settings):
        super(Hello, self).Step(settings)
        self.body.ApplyForce(force=(2,0), point=self.body.worldCenter, wake=True)  # any force applied not at cog converts to torque

if __name__ == "__main__":
    main(Hello)
