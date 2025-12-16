import math
from data_generation.constants import *

COMFORT_BALL_DEFAULT_CONFIG = {
    "variation": "default",
    "name": None,
    "num_steps": 37,
    "save_path": None,

    "ref_shape": SPHERE,
    "ref_color": BLUE,
    "ref_size": 0.5,
    "ref_position": (0, 0, 0.5),
    "ref_rotation": (0, 0, 0),

    "var_shape": SPHERE,
    "var_color": RED,
    "var_size": 0.4,
    "var_position": (0, 0, 0.4),
    "var_rotation": (0, 0, 0),

    "num_distractors": 0,
    "cam_position": None,
}
# ref : 0.3,0.4,0.5
# ==> 비율 맞춰서 다양하게

# 1260
# addressee 없으면 6개 각도에 대해서 1260개

#6*15*14 = 720
#6*10*9 = 540

# addressee 있으면 6개 각도, 색 조합 210개 => 100개만 뽑기 , object 12개 ==> 색 별로 3개만 random으로, 좌우 2개 총 3600개
#6*2*3*10*9 = 


# 1260개
# 36개 ==> 100초(1분 40초), 3600개 ==> 10000초(166분, 2시간 46분), 1260개 ==> 3500초(58분)



COMFORT_BALL_RELATIONS = {
    BEHIND: {
        "relation": BEHIND,
        "path_type": "rotate",
        "radius": 2.9,
        "angle_range": (180, 180+360),
    }
}

"""
    FRONT: {
        "relation": FRONT,
        "path_type": "rotate",
        "radius": 2.9,
        "angle_range": (0, 360),
    },
    LEFT: {
        "relation": LEFT,
        "path_type": "rotate",
        "radius": 2.9,
        "angle_range": (90, 90+360),
    },
    RIGHT: {
        "relation": RIGHT,
        "path_type": "rotate",
        "radius": 2.9,
        "angle_range": (270, 270+360),
    }
"""




COMFORT_BALL_VARIATIONS = [
        {"variation": "6angles_colors_noise_addressee", "angle_list": [350, 10, 170, 190], "var_size_list":[0.225, 0.225, 0.6, 0.6],
        "ref_size_list": [0.6, 0.6, 0.3, 0.3], 
        "radius_list": [2.0, 2.0, 4.0, 4.0],
        "noise": {
        "var_size_eps": 0.1,          # 각 step 크기에 ±이만큼 지터0.6
        "radius_eps":  0.4,           # 궤도 반지름에 ±이만큼 지터
        "cam_eps":     (0, 0, 1.5) # 카메라 위치 x,y,z에 각각 ±이만큼 지터
        },
        "addressee": True,
#        "addressee_shape": SOPHIA,
#        "addressee_size": 0.015,
#        "addressee_position": (0.0, -3.0, 0.1),   # 왼쪽(-x)1
#        "addressee_rotation": (90, 0, 90),     # +x(중심) 바라보게
        },

        
        {"variation": "6angles_colors_noise", "angle_list": [330, 30, 150, 210], "var_size_list":[0.35, 0.35, 1.0, 1.0]
,
        "ref_size_list": [0.8, 0.8, 0.5, 0.5], 
        "radius_list": [2.75, 2.75, 4.0, 4.0],
        "noise": {
        "var_size_eps": 0.1,          # 각 step 크기에 ±이만큼 지터0.6
        "radius_eps":  0.4,           # 궤도 반지름에 ±이만큼 지터
        "cam_eps":     (0, 0, 0) # 카메라 위치 x,y,z에 각각 ±이만큼 지터
        },
        "addressee" : False
        },

]
"""
        {"variation": "6angles_colors_noise_addressee", "angle_list": [330, 0, 30, 150, 180, 210], "var_size_list":[0.225, 0.225, 0.225, 0.6, 0.6, 0.6],
        "ref_size_list": [0.6, 0.6, 0.6, 0.3, 0.3, 0.3], 
        "radius_list": [2.0, 2.5, 2.0, 4.0, 4.0, 4.0],
        "noise": {
        "var_size_eps": 0.1,          # 각 step 크기에 ±이만큼 지터0.6
        "radius_eps":  0.4,           # 궤도 반지름에 ±이만큼 지터
        "cam_eps":     (0, 0, 1.5) # 카메라 위치 x,y,z에 각각 ±이만큼 지터
        },
        "addressee": True,
#        "addressee_shape": SOPHIA,
#        "addressee_size": 0.015,
#        "addressee_position": (0.0, -3.0, 0.1),   # 왼쪽(-x)1
#        "addressee_rotation": (90, 0, 90),     # +x(중심) 바라보게
        },




        {"variation": "6angles_colors_noise", "angle_list": [330, 0, 30, 150, 180, 210], "var_size_list":[0.35, 0.15, 0.35, 1.0, 1.0, 1.0]
,
        "ref_size_list": [0.8, 0.8, 0.8, 0.5, 0.35, 0.5], 
        "radius_list": [2.75, 4, 2.75, 4.0, 6.0, 4.0],
        "noise": {
        "var_size_eps": 0.1,          # 각 step 크기에 ±이만큼 지터0.6
        "radius_eps":  0.4,           # 궤도 반지름에 ±이만큼 지터
        "cam_eps":     (0, 0, 0.4) # 카메라 위치 x,y,z에 각각 ±이만큼 지터
        },
        "addressee" : False
        },


    {"variation": "6angles_colors", "angle_list": [350, 0, 10, 170, 180, 190], "var_size_list":[0.45, 0.45, 0.45, 0.75, 0.75, 0.75]},
    {"variation": "6angles", "angle_list": [350, 0, 10, 170, 180, 190], "var_size_list":[0.45, 0.45, 0.45, 0.75, 0.75, 0.75]},

    {"variation": "default"},
    {"variation": "color", "var_color": YELLOW, "ref_color": GREEN},
    {"variation": "size", "var_size": 0.7, "ref_size": 0.45},
    {"variation": "cam_position", "cam_position": (9.0, 0.0, 0)}

#    {"variation": "distractor", "num_distractors": 1},
"""