import sys
from data_generation.constants import *

import random

WOMAN_DEFAULT_SIZE = 0.6   # WOMAN_CFG['size']와 동일
WOMAN_X = 3.0
WOMAN_DEFAULT_Z = 0.05


def _jitter(val, eps):
    # eps가 스칼라면 스칼라 지터
        return val + random.uniform(-eps, eps)

def _jitter_vec3(vec, eps_xyz):
    ex, ey, ez = eps_xyz
    return (vec[0] + random.uniform(-ex, ex),
            vec[1] + random.uniform(-ey, ey),
            vec[2] + random.uniform(-ez, ez))


def custom_variations(relation, variation, default_config, relation_config_copy, dataset_name=None):
    if dataset_name == "comfort_ball":
        if relation in ROTATION_LIST:
            if variation['variation'] == "size":
                relation_config_copy['ref_position'] = (0, 0, variation['ref_size'])
                relation_config_copy['var_position'] = (0, 0, variation['var_size'])
            
            if variation['variation'] == "angle_custom":
                angle_list = variation.get("angle_list")
                if angle_list:
                    # 리스트로 보장 및 복사
                    relation_config_copy["angle_list"] = list(angle_list)
                    # 각도 개수만큼 스텝 수를 덮어써서 균등 분할 로직이 개입하지 않도록 함
                    relation_config_copy["num_steps"] = len(angle_list)


            # ---- addressee 배치 추가 ----
            if variation.get("addressee"):
                relation_config_copy["addressee"]          = True
                relation_config_copy["addressee_shape"]    = variation["addressee_shape"]
                relation_config_copy["addressee_size"]     = variation["addressee_size"]
                relation_config_copy["addressee_position"] = tuple(variation["addressee_position"])
                relation_config_copy["addressee_rotation"] = tuple(variation["addressee_rotation"])
                

            # ✅ ref_size_list가 있으면 z를 맞춘 ref_position_list를 만들어 준다
            if "ref_size_list" in variation and variation["ref_size_list"]:
                variation["ref_position_list"] = [(0.0, 0.0, s) for s in variation["ref_size_list"]]
            if "var_size_list" in variation and variation["var_size_list"]:
                variation["var_position_list"] = [(0.0, 0.0, s) for s in variation["var_size_list"]]

            # ------- 여기부터 노이즈 주입 파트 추가 -------
            noise = variation.get("noise")
            if noise:
                # 1) radius 노이즈: relation_config에 들어있는 반지름에 지터
                if "radius_eps" in noise and "radius" in relation_config_copy and "radius_list" not in variation:
                    base_r = relation_config_copy["radius"]
                # step 수 결정 (angle_list 있으면 그 길이, 아니면 num_steps)
                    if "angle_list" in relation_config_copy and relation_config_copy["angle_list"]:
                        steps = len(relation_config_copy["angle_list"])
                    else:
                        steps = relation_config_copy.get("num_steps") or default_config.get("num_steps") or 1

                    # ✅ step별 radius 리스트 만들기
                    variation["radius_list"] = [
                        max(0.0, _jitter(base_r, noise["radius_eps"])) for _ in range(steps)
                    ]

                # 2) cam_position 노이즈: 우선순위는 variation > default_config
                if "cam_eps" in noise:
                    cam_eps = noise["cam_eps"]

                    # 베이스 카메라 위치 찾기
                    base_cam = None
                    if variation.get("cam_position") is not None:
                        base_cam = tuple(variation["cam_position"])
                    elif default_config.get("cam_position") is not None:
                        base_cam = tuple(default_config["cam_position"])
                    else:
                        # 마지막 fallback (예: comfort_ball 기준값)
                        base_cam = (7.8342, 0.0, 3.6126)

                    # step 수 결정
                    if "angle_list" in relation_config_copy and relation_config_copy["angle_list"]:
                        steps = len(relation_config_copy["angle_list"])
                    else:
                        steps = relation_config_copy.get("num_steps") or default_config.get("num_steps") or 1

                    # ✅ step마다 다른 카메라 위치를 만든다
                    variation["cam_position_list"] = [
                        _jitter_vec3(base_cam, cam_eps) for _ in range(steps)
                    ]

                    # (원하면 variation["cam_position"]는 안 써도 되지만, 남겨도 무방)


                #    variation["cam_position"] = _jitter_vec3(base_cam, noise["cam_eps"])

                # 3) var_size 노이즈: var_size_list가 있으면 step별로 지터, 없으면 단일 var_size 지터
                if "var_size_eps" in noise:
                    eps = noise["var_size_eps"]
                    if "var_size_list" in variation and variation["var_size_list"]:
                        base_list = variation["var_size_list"]
                        # 음수/0 방지
                        new_sizes = [max(0.01, _jitter(s, eps)) for s in base_list]
                        variation["var_size_list"] = new_sizes
                        variation["var_position_list"] = [(0.0, 0.0, s) for s in new_sizes]
            # ------- 노이즈 주입 끝 -------

            return relation_config_copy  # (네 기존 반환 방식 유지)
        