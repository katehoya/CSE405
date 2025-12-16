# COMFORT BALL ASSETS
SPHERE = "Sphere"

# COMFORT CAR ASSETS
BICYCLE_MOUNTAIN = "bicycle_mountain"
CAR_SEDAN = "car_sedan"
COUCH = "Sofa"
BASKETBALL = "Basketball"
CHAIR = "Chair"
DOG = "Dog"
BED = "Bed"
DUCK = "Duck"
LAPTOP = "Laptop"
HORSE_L = "HorseL"
HORSE_R = "HorseR"
BENCH = "Bench"
SNOWMAN = "Snowman"
PENGUIN = "Penguin"
CAT = "Cat"
HORSE = "Horse"
CAMEL = "Camel"
REFRIGERATOR = "Refrigerator"

SOPHIA = "Sophia" # addressee

SPECIAL = [SOPHIA, COUCH, BASKETBALL, CHAIR, DOG, BED, DUCK, LAPTOP, HORSE_L, HORSE_R, BENCH, PENGUIN, SNOWMAN, CAT, HORSE, CAMEL, REFRIGERATOR]


# define color codes
RED = (1, 0, 0, 1)
GREEN = (0, 1, 0, 1)
BLUE = (0, 0, 1, 1)
YELLOW = (1, 1, 0, 1)
PURPLE = (1, 0, 1, 1)
ORANGE = (1, 0.5, 0, 1)
CYAN = (0, 1, 1, 1)
GRAY = (0.5, 0.5, 0.5, 1)
DARK_GRAY = (0.1, 0.1, 0.1, 1)
WHITE = (1, 1, 1, 1)
AIRPLANE_WHITE = (0.937, 0.937, 0.957, 1)
CHARCOAL_GRAY = (0.3, 0.3, 0.3, 1)
CAR_RED = (0.95, 0.1, 0.1, 1)
CAR_BLUE = (0.1, 0.3, 0.9, 1)
BLACK = (0, 0, 0, 1)

COLOR_PAIRS = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE, CYAN, GRAY, WHITE, BLACK] 

# white-gray, yellow-orange, black-gray 싹 다 빼기
# 10 * 9 * 4  =  
# 8 7 4  = 226

# AIRPLANE_WHITE,CHARCOAL_GRAY, CAR_RED, CAR_BLUE,DARK_GRAY
COLORS = {
    "RED": [RED, CAR_RED],
    "GREEN": [GREEN],
    "BLUE": [BLUE, CAR_BLUE],
    "YELLOW": [YELLOW],
    "PURPLE": [PURPLE],
    "GRAY": [GRAY, CHARCOAL_GRAY],
    "WHITE": [WHITE],
    "ORANGE": [ORANGE],
    "CYAN": [CYAN],
    "BLACK": [BLACK],
}


BICYCLE_MOUNTAIN_CFG = {
    "shape" : BICYCLE_MOUNTAIN,
    "color" : DARK_GRAY,
    "direction" : (90, 0, 0),
    "size" : 2.5,
    "z" : 0.8,
}

HORSE_CFG = {
    "shape" : HORSE,
    "color" : "",
    "direction" : (0, 0, 270),
    "size" : 0.8,
    "z" : 1.0,
}
CAR_SEDAN_CFG = {
    "shape" : CAR_SEDAN,
    "color" : AIRPLANE_WHITE,
    "direction" : (90, 0, 270),
    "size" : 2.2,
    "z" : 0.95,
}

COUCH_CFG = {
    "shape" : COUCH,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 1.0,
    "z" : 0,
}

CHAIR_CFG = {
    "shape" : CHAIR,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 1.7,
    "z" : 0.9,
}

DOG_CFG = {
    "shape" : DOG,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 1.0,
    "z" : 0.6,
}

BED_CFG = {
    "shape" : BED,
    "color" : "",
    "direction" : (0, 0, 0),
    "size" : 1.3,
    "z" : 0.5,
}


DUCK_CFG = {
    "shape" : DUCK,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 2,
    "z" : 0.35,
}

PENGUIN_CFG = {
    "shape" : PENGUIN,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 1.8,
    "z" : 1.0,
}

LAPTOP_CFG = {
    "shape" : LAPTOP,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 3,
    "z" : 0.4,
}

BENCH_CFG = {
    "shape" : BENCH,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 1.25,
    "z" : 0.6,
}

WOMAN_CFG = {
    "shape" : SOPHIA,
    "color" : "",
    "direction" : (90, 0, 0),
    "size" : 0.015,
    "z" : 0.05,
}

SNOWMAN_CFG = {
    "shape" : SNOWMAN,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 0.25,
    "z" : 1.2,
}

CAT_CFG = {
    "shape" : CAT,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 0.6,
    "z" : 0.4,
}

CAMEL_CFG = {
    "shape" : CAMEL,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 1.0,
    "z" : 1.0,
}

REFRIGERATOR_CFG = {
    "shape" : REFRIGERATOR,
    "color" : "",
    "direction" : (0, 0, 90),
    "size" : 1.5,
    "z" : 1.5,
}

DEFAULT_DICT = [COUCH_CFG, CHAIR_CFG, DOG_CFG, DUCK_CFG, PENGUIN_CFG, LAPTOP_CFG, WOMAN_CFG, CAT_CFG, REFRIGERATOR_CFG, HORSE_CFG, CAMEL_CFG, SNOWMAN_CFG]

def color_to_name(color):
    """Convert a color value to its name."""
    for name, value in COLORS.items():
        if color in value:
            return name.lower()
    return "unknown"


BEHIND = "behind"
FRONT = "infrontof"
LEFT = "totheleft"
RIGHT = "totheright"

ROTATION_LIST = [BEHIND, FRONT, LEFT, RIGHT]
ALL_RELATIONS = ROTATION_LIST

BASE_SCENE = "data_generation/assets/base_scene_centered.blend"
MATERIAL_DIR = "data_generation/materials/"
SHAPE_DIR = "data_generation/assets/"

IM_SIZE = 512

