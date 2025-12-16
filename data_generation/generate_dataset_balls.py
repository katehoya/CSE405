import os
import sys
sys.path.append(os.getcwd())

import copy
import json
import argparse

import cv2
import numpy as np

from data_generation.utils import render_scene_config   

from data_generation.constants import *
from data_generation.custom_variations import custom_variations
from data_generation.comfort_ball_config import *

import itertools
import random
import math



def parse_args():
    parser = argparse.ArgumentParser(description="Render scene configuration script")
    parser.add_argument(
        '--dataset_name', type=str, required=True, 
        help="Dataset name to specify the configuration (comfort_ball, comfort_car_left, comfort_car_right)"
    )
    parser.add_argument('--debug', action='store_true', help="Enable debug mode")
    parser.add_argument('--save_path', type=str, default=None, help="Path to save the rendered images")
    # 핵심: Blender 실행 시에는 전체 argv에 Blender 옵션이 섞여있음.
    # '--' 이후의 것만 우리 스크립트 인자로 파싱해야 함.
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    return parser.parse_args(argv)
#    return parser.parse_args()

def sample_unique_pairs(arr, n, seed=None, dedup_values=True):

    if dedup_values:
        try:
            # hashable 원소에 한해 값 기준 고유화(원본 순서 보존)
            arr = list(dict.fromkeys(arr))
        except TypeError:
            # dict 등 unhashable 원소가 있으면 고유화는 건너뜀(인덱스 기준으로는 서로 다르게 선택될 수 있음)
            pass

    if len(arr) < 2:
        raise ValueError("원소가 최소 2개는 있어야 합니다.")

    # 순서를 고려한 3-순열 전체 생성
    # 개수: P(len(arr), 3) = len(arr) * (len(arr)-1) * (len(arr)-2)
    all_perms = list(itertools.permutations(arr, 2))
    total = len(all_perms)
    if n > total:
        raise ValueError(f"요청 n={n} > 가능한 순열 수 {total}")

    rng = random.Random(seed)
    rng.shuffle(all_perms)
    return all_perms[:n]

def adjust_direction(base_direction, side):
    # degree tuple -> rad array
    rx, ry, rz = base_direction
    if side == "left":
        rz += 90   # 좌측 바라보기 → 왼쪽(Y-) 쪽을 보게 yaw +90
    elif side == "right":
        rz -= 90   # 우측 바라보기 → 오른쪽(Y+) 쪽을 보게 yaw -90
    return (rx, ry, rz)

def expand_color_pairs(variations, color_candidates, n=None, seed=42):
    """
    variations 목록에서 {"variation": "6angles_colors", ...} 항목을 찾아
    color_candidates의 모든 순서 있는 페어(또는 샘플링된 페어)로 확장해 반환.
    """
    expanded = []
    # 전체 페어(순서 고려) = permutations(arr, 2)
    all_pairs = list(itertools.permutations(color_candidates, 2))

    # 필요하면 샘플링 (원하는 수 n개만)
    if n is not None:
        # 네가 만든 함수 사용
        pairs = sample_unique_pairs(color_candidates, n=n, seed=seed, dedup_values=True)
    else:
        pairs = all_pairs

    for v in variations:

        if v.get("variation") == "6angles_colors_noise":
            for var_c, ref_c in pairs:
                new_v = {**v, "var_color": var_c, "ref_color": ref_c}           
                new_v["addressee"] = False  # 명시적으로 False
                expanded.append(new_v)

        if v.get("variation") == "6angles_colors_noise_addressee":
            # 이 variation은 angle_list/var_size_list 같은 고정 속성을 유지하면서
            # (var_color, ref_color)만 바꿔가며 확장
            for var_c, ref_c in pairs:
                # addressee
                SELECTED_ADDRESSEES = random.sample(DEFAULT_DICT, 3)
                for addr in SELECTED_ADDRESSEES:   # 랜덤 뽑힌 3개
                    for side in ["left", "right"]:  # 양쪽 방향
                        new_v = {**v, "var_color": var_c, "ref_color": ref_c}
                        new_v["addressee"] = True
                        new_v["addressee_shape"] = addr["shape"]
                        new_v["addressee_size"] = addr["size"]
                        if side == "left":
                            new_v["addressee_position"] = (0.0, -2.5, addr["z"])
                            new_v["addressee_rotation"] = adjust_direction(addr["direction"], "left")
                        #    new_v["variation"] = f"{v['variation']}_{addr['shape']}_left"
                        else:
                            new_v["addressee_position"] = (0, 2.5, addr["z"])
                            new_v["addressee_rotation"] = adjust_direction(addr["direction"], "right")
                        #    new_v["variation"] = f"{v['variation']}_{addr['shape']}_right"                    
                        expanded.append(new_v)
        else:
            expanded.append(v)
    return expanded


if __name__ == "__main__":
    args = parse_args()

    if args.dataset_name == "comfort_ball":
        default_config = COMFORT_BALL_DEFAULT_CONFIG
        variations = COMFORT_BALL_VARIATIONS
        relations = COMFORT_BALL_RELATIONS
        dataset_name = "comfort_ball"

    if args.dataset_name == "comfort_ball_colors":
        default_config = COMFORT_BALL_DEFAULT_CONFIG
        variations = expand_color_pairs(
            variations=COMFORT_BALL_VARIATIONS,
            color_candidates=COLOR_PAIRS,  # constants에 있는 리스트
            n=None,                        # 전부 쓰려면 None, 일부만 뽑으려면 정수 (예: 40)
            seed=42
        )
        relations = COMFORT_BALL_RELATIONS
        dataset_name = "comfort_ball"

    if args.dataset_name == "comfort_ball_noises":
        default_config = COMFORT_BALL_DEFAULT_CONFIG
        variations = expand_color_pairs(
            variations=COMFORT_BALL_VARIATIONS,
            color_candidates=COLOR_PAIRS,
            n=None,                        
            seed=42
        )
        relations = COMFORT_BALL_RELATIONS
        dataset_name = "comfort_ball"       
    else:
        raise ValueError("Invalid dataset name")


    default_config["save_path"] = os.path.join(args.save_path, dataset_name)
    global_idx = 0

    for relation, relation_config in relations.items(): # relation : key(BEHIND, FRONT...), relation_config : value("relation" : ...., "", ...)
        distractors = []
        for variation in variations:
            if args.debug:
                variation["num_steps"] = 3

            relation_config_copy = copy.deepcopy(relation_config)
            relation_config_copy = custom_variations(relation, variation, default_config, relation_config_copy, dataset_name=dataset_name)
            config = {**default_config, **variation, **relation_config_copy}
            print(f"Variation: {variation['variation']} | Relation: {relation}", file=sys.stderr)

            config.pop("noise", None)

            print({
            "variation": variation.get("variation"),
            "addressee?": config.get("addressee"),
            "addr_shape": config.get("addressee_shape"),
            "addr_pos":   config.get("addressee_position"),
            "addr_rot":   config.get("addressee_rotation"),
            }, file=sys.stderr)


            # 블렌더로 rendering scene
            mapping, distractors, global_idx = render_scene_config(  
                **config,
                distractors=distractors,
                dataset_name=dataset_name,
                render_shadow=True,
                cuda=False,
                global_idx=global_idx
            )

            output_path = os.path.join(args.save_path, dataset_name, relation, variation['variation'])



    """
            # 마지막 composite image 합성
            if not args.debug:
                images = [cv2.imread(os.path.join(output_path, f'{i}.png')) for i in range(4)]
                indices = [0, 9, 18, 27]
                images = [cv2.imread(os.path.join(output_path, f'{I}.png')) for I in indices]
                height, width, channels = images[0].shape
                composite_image = np.zeros((height * 2, width * 2, channels), dtype=np.uint8)
                composite_image[0:height, 0:width] = images[0]       # Top-left
                composite_image[0:height, width:width*2] = images[1] # Top-right
                composite_image[height:height*2, 0:width] = images[2] # Bottom-left
                composite_image[height:height*2, width:width*2] = images[3] # Bottom-right
                cv2.imwrite(os.path.join(output_path, 'composite_image.png'), composite_image)
                print(f"Saved composite image to {os.path.join(output_path, 'composite_image.png')}", file=sys.stderr)

            # config.json 파일 합성
            os.makedirs(output_path, exist_ok=True)
            config_path = os.path.join(output_path, f"config.json")
            with open(config_path, 'w') as f:
                config_copy = copy.deepcopy(config)
                config_copy['var_color'] = color_to_name(config['var_color'])
                config_copy['ref_color'] = color_to_name(config['ref_color'])
                config_copy['mapping'] = mapping
                if distractors is not None and not isinstance(distractors, str):
                    for distractor in distractors:
                        distractor['location'] = np.array(distractor['location']).tolist()
                        distractor['dimensions'] = np.array(distractor['dimensions']).tolist()
                        distractor['color'] = color_to_name(distractor['color'])
                        distractor['position'] = np.array(distractor['position']).tolist()
                # print(distractors, file=sys.stderr)
                config_copy['distractor'] = distractors
                # assert(len(mapping) == DEFAULT_CONFIG["num_steps"])

                json.dump(config_copy, f, indent=4)                
    """