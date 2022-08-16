class FrameworkSettings:
    # The default backend to use in (can be: pyglet, pygame, etc.)
    backend = 'pygame'

    # Physics options
    hz = 30.0
    velocityIterations = 4
    positionIterations = 2
    # Makes physics results more accurate (see Box2D wiki)
    enableWarmStarting = True
    enableContinuous = True     # Calculate time of impact
    enableSubStepping = False

    # Drawing
    drawStats = True
    drawShapes = True
    drawJoints = False
    drawCoreShapes = False
    drawAABBs = False
    drawOBBs = False
    drawPairs = False
    drawContactPoints = False
    maxContactPoints = 100
    drawContactNormals = False
    drawFPS = True
    drawMenu = True             # toggle by pressing F1
    drawCOMs = False            # Centers of mass
    pointSize = 2.0             # pixel radius for drawing points

    # Miscellaneous testbed options
    pause = False
    singleStep = False
    # run the test's initialization without graphics, and then quit (for
    # testing)
    onlyInit = False

    # Initial view options
    zoom = 5.5  # smaller = zoom out
    window_size = (1280, 720)

class WorldSettings:

    init_podds = 1

    # food
    spawn_food_interval = 0.5 * FrameworkSettings.hz  # number of frames/steps
    grid = 10  # smaller -> food spawn further apart
    spawn_food_box = 60 * grid
    init_food = 200
    max_food = 4000
    food_energy = 10  # can be genetically determined in the future

    # sunlight
    sunlight_energy = 10 / FrameworkSettings.hz

    # movement
    turn_scale = 0.5  # ratio of turning force to forward force

    # border
    enable_border = True
    rounded_corners = False

    # TEST
    test_density = 1

class PoddSettings:
    # energy
    init_energy = 30
    max_energy = 60
    age_factor = 0.2 / FrameworkSettings.hz  # how quickly do the podds minimum energy rises in response to age
    ec_moving = 1 / FrameworkSettings.hz # energy consumed per second to move
    ec_living = 0.5 / FrameworkSettings.hz # energy consumed per second to continue living

    # reproduction
    birth_cost = 35  # energy cost in giving birth
    birth_age = 8  # minimum age to give birth in seconds

    # mutation
    mut_rate = 0.5
    mut_sd = 0.05  # variance in mutation

class BrainSettings:
    # nodes
    n_inputs = 6
    n_outputs = 3
    max_node = 9999

    # mutation chance
    chance_new = 0.25  # chance at each new_genome of creating a new connection
    chance_del = 0.05  # chance of each existing connection of deleting itself
    
    # mutation strength: adjusting weights
    mut_sd = 0.05
    min_mut_weight = 0.001  # if abs(weight) of connection is less than this number, any mutation will continue assuming this minimum value of weight (prevent 0 weight problem)