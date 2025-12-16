import math
from data_generation.constants import *

import random
import itertools

def sample_unique_triplets(arr, n, seed=None, dedup_values=True):
    """
    arr에서 '값' 기준으로(옵션) 중복 제거 후,
    순서를 고려한 길이 3의 순열을 무작위로 n개 반환합니다.
    - 내부 3개 원소는 모두 달라야 함
    - 같은 원소 셋이라도 순서가 다르면 다른 것으로 간주
    - 반환: list[tuple], 각 tuple 길이 = 3
    """
    if dedup_values:
        try:
            # hashable 원소에 한해 값 기준 고유화(원본 순서 보존)
            arr = list(dict.fromkeys(arr))
        except TypeError:
            # dict 등 unhashable 원소가 있으면 고유화는 건너뜀(인덱스 기준으로는 서로 다르게 선택될 수 있음)
            pass

    if len(arr) < 3:
        raise ValueError("원소가 최소 3개는 있어야 합니다.")

    # 순서를 고려한 3-순열 전체 생성
    # 개수: P(len(arr), 3) = len(arr) * (len(arr)-1) * (len(arr)-2)
    all_perms = list(itertools.permutations(arr, 3))
    total = len(all_perms)
    if n > total:
        raise ValueError(f"요청 n={n} > 가능한 순열 수 {total}")

    rng = random.Random(seed)
    rng.shuffle(all_perms)
    return all_perms[:n]

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


COMFORT_VISIBILITY_CONFIG = {
    "num_distractors": 0,
    "name": None,
    "num_steps": 2
}

# Positional attributes
COMFORT_VISIBILITY_RELATIONS = {
    # Rotation relations
    FRONT: {
        "relation": FRONT,
        "path_type": "rotate",
        "angle_range": (0, 0),
    },
}

COMFORT_VISIBILITY_VARIATIONS = []

n = 320
triplets = sample_unique_triplets(DEFAULT_DICT, n=n, seed=42)



for idx, t in enumerate(triplets):
    if idx == n:
        break

    
    if idx < n//2 and idx%2==0:
        ref_rot = 90
        var_pose = 2.5
        result = "visible"
    elif idx < n//2 and idx%2==1:
        ref_rot = -90
        var_pose = -2.5
        result = "visible"

    elif idx >= n//2 and idx%2==0:
        ref_rot = 90
        var_pose = -2.5
        result = "not"
    
    elif idx >= n//2 and idx%2==1:
        ref_rot = -90
        var_pose = 2.5
        result = "not"

    var_rot = random.randint(0, 360)
    x_noise = random.uniform(-0.2, 0.2)
    y_noise = random.uniform(-0.2, 0.2)

    ref = t[0]["shape"]
    var = t[1]["shape"]
    add = t[2]["shape"]

    COMFORT_DICT = {
        # render config
        "variation": f"{ref}_{var}_{add}_{ref_rot}_{result}",
        "num_steps": 2,
        "radius": 2.5,

        # ref object config
        "ref_shape": t[0]["shape"],
        "ref_color": t[0]["color"],
        "ref_size": t[0]["size"],
        "ref_position": (0, 0, t[0]['z']),
        "ref_rotation": (t[0]["direction"][0], t[0]["direction"][1], t[0]["direction"][2] + ref_rot),

        # var object config
        "var_shape": t[1]["shape"],
        "var_color": t[1]["color"],
        "var_size": t[1]["size"],
        "var_position": (-2 + x_noise, var_pose + y_noise, t[1]['z']),
        "var_rotation": (t[1]["direction"][0], t[1]["direction"][1], t[1]["direction"][2] + var_rot),

        # addressee object config
        "addressee": False,

        # variation config
        "num_distractors": 0,
        "cam_position": (12.0, 0.0, 3.0),    
    }

    COMFORT_VISIBILITY_VARIATIONS.append(COMFORT_DICT)


