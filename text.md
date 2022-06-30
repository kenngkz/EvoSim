# Planning

## General Approach
Start with only blueprint genes (like Bibites) to avoid neural network calculations. Continuous gene values instead of binary. After working simulation for blueprint, change to recipe type genes: genes only include existence of connections, weights must be trained. Other genes can also be converted to recipe - dependent on environment, childhood period.

Start with Python first, later move to faster language like Rust. Work out how the simulation will be done and later on port to other language.

How are genes read? Different positions in the genome are intepreted to have different direct effects, possibly allow the translation of gene to attribute to change (eg change gene1 encoding for size to gene1 encoding for speed)

## Map design
Grid structure, all objects in the simulation take up a certain space/number of grids (possibly dependent on size gene/attribute). Shape initially square, later on can take different shapes

## Map display
pygame interface. Construct simple bodies using shapes + colours

## Collision
outsourced to pybox2d

## Gene representation
1. connection - (from_node, to_node, weight)
2. node - (node_id, status): status represents whether node is active or not
3. attr - ? : make this expandable to add new attr in the future
    - speed
    - vision range
    - type of food digestion
    - size

## Podd observation space
https://github.com/pybox2d/pybox2d/blob/master/library/Box2D/examples/edge_shapes.py
raycast from point (either "eye" or centre of podd) in a pi/2 (~1.6) radians field and with ray spacing 0.05 (32 rays). Range, Field and Detail can be genetically modified in the future.
If ray hit, show distance to object + colour of object. (64 vision inputs)

## Movement
https://github.com/pybox2d/pybox2d/blob/master/library/Box2D/examples/apply_force.py
Podd object determines the action to take (turn, move forward, slow down), pass intructions to world and apply force to move

## How to do NN calculations
1. numpy/tensorflow will not be the best for dynamic connections architecture.
2. with manual calculation, will be very slow (i think)
    - can speed it up with numba?

## Attributes
1. Brain
2. Size
3. Strength
4. Vision
5. Aging
6. Defense (density)
7. Damage (?) - work in combination with strength
8. Diet