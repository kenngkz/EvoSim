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
    food_energy = 18  # can be genetically determined in the future

    # sunlight
    sunlight_energy = 16 / FrameworkSettings.hz

    # movement
    turn_scale = 0.5  # ratio of turning force to forward force

    # border
    enable_border = True
    rounded_corners = False

    # TEST
    test_density = 1

class PoddSettings:
    # energy
    init_energy = 40
    max_energy = 80
    age_factor = 0.2 / FrameworkSettings.hz  # how quickly do the podds minimum energy rises in response to age
    ec_moving = 2 / FrameworkSettings.hz # energy consumed per frame to move
    ec_living = 0.5 / FrameworkSettings.hz # energy consumed per frame to continue living
    ec_factor_brain = 0.05 / FrameworkSettings.hz  # energy consumed per frame per point of brain complexity
    ec_factor_size = 1 / FrameworkSettings.hz  # energy consumed per frame per point of size
    ec_factor_str = 1 / FrameworkSettings.hz  # energy consumer per frame per point of strength

    # reproduction
    birth_cost = 50  # energy cost in giving birth
    # birth_age = 8  # minimum age to give birth in seconds

    # age death
    fixed_death_rate = 0.0 / FrameworkSettings.hz  # death chance per frame
    age_deterioration = 0.0002 /FrameworkSettings.hz  # death chance per frame scaling in response to age
        # let sudden death occur in response to energy: scale ** (-0.1*x)
        # scale controls how quickly sudden death rate drops in response to higher energy: higher scale means drops faster
        # alternatively, make the death rate only kick in at lower energy levels (maybe bottom 10%) and scale within that range

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