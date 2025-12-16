import os
import re
import shutil
import csv

import random
import string
import base64
import cv2

def generate_unique_qids(n):
    # 사용할 문자 집합 (대문자 + 숫자)
    charset = string.ascii_uppercase + string.digits

    qids = set()
    while len(qids) < n:
        qid = ''.join(random.choices(charset, k=8))
        qids.add(qid)  # set이므로 자동 중복 제거

    return list(qids)

def encode_image_to_base64(img_path: str) -> str:
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

# --- ADDED: 좌우반전 이미지를 생성/저장하는 유틸
FLIP_SUBDIR = "_flipped"  # 각 이미지 폴더 아래에 생성
def get_flipped_save_path(src_img_path: str) -> str:
    """원본 이미지 경로를 받아 flip 결과 저장 경로를 돌려준다."""
    dirpath, fname = os.path.split(src_img_path)
    name, ext = os.path.splitext(fname)
    out_dir = os.path.join(dirpath, FLIP_SUBDIR)
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, f"{name}_flip{ext}")

def ensure_flipped_image(src_img_path: str) -> str:
    """원본을 좌우반전해서 저장하고, 저장된 경로를 반환. 이미 있으면 재사용."""
    out_path = get_flipped_save_path(src_img_path)
    if not os.path.exists(out_path):
        img = cv2.imread(src_img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise FileNotFoundError(f"Failed to read image for flipping: {src_img_path}")
        flipped = cv2.flip(img, 1)  # 1: 좌우반전
        # PNG/JPG 모두 확장자에 맞춰 저장됨
        cv2.imwrite(out_path, flipped)
    return out_path


fields = ["index", "qid", "question", "A", "B", "C", "D", "answer", "category", "image"]
rows = []
rows_aug = []

# 받아오는 image 경로가 다름
task1 = 'COMFORT_only_balls'
task2 = 'COMFORT_balls_addressee'

img_dir1 = f"data/comfort_ball/behind/{task1}"
img_dir2 = f"data/comfort_ball/behind/{task2}"

# 저장되는 tsv 파일은 하나.
output_tsv = f"data/comfort_ball/scripts/COMFORT_script.tsv"

# ====== 추가: 샘플 개수 & 시드 ======
N1 = 200   # imgs1에서 뽑을 개수 (원하는 수로)
N2 = 400   # imgs2에서 뽑을 개수 (원하는 수로)
SEED = 42  # 재현성 보장용 시드
rng = random.Random(SEED)

imgs1_all = [f for f in os.listdir(img_dir1) if f.lower().endswith((".png",".jpg",".jpeg"))]
imgs2_all = [f for f in os.listdir(img_dir2) if f.lower().endswith((".png",".jpg",".jpeg"))]


imgs_infront = rng.sample(imgs1_all, N1)
imgs_closer = rng.sample(imgs1_all, N1)
imgs2 = rng.sample(imgs2_all, N2)

imgs_infront.sort()
imgs_closer.sort()
imgs2.sort()

#qid_all = generate_unique_qids(N1*2)
qid_all = generate_unique_qids(N1*2 + N2)

qid_list1 = qid_all[:N1]
qid_list2 = qid_all[N1:N1*2]
qid_list3 = qid_all[N1*2:]




########### front_behind
for i, img in enumerate(imgs_infront):
    img_path = os.path.join(img_dir1, img)

    # 1. 확장자 제거
    name_without_ext = img.rsplit(".", 1)[0]

    # 2. "_" 기준으로 분리
    parts = name_without_ext.split("_")
    print(parts)

    #0000_green_red_350.0
    
    img_b64 = encode_image_to_base64(img_path)
    angle_token = parts[-1].split(".")[0]

    # in front of, behind
    dict_infrontof = {
#        "index" : i,
        "qid" : qid_list1[i],
        "question": f"From the camera's perspective, which object is located in front of, the {parts[1]} ball or the {parts[2]} ball?",
        "A" : f"{parts[1]}",
        "B" : f"{parts[2]}",
        "C" : "",
        "D" : "",
        "answer" : "A" if angle_token in ("350", "0", "10", "330", "30") else "B",
        "category" : "front_behind",
        "image" : img_b64
    }

    dict_infrontof_circ = {
#        "index" : i,
        "qid" : f"{qid_list1[i]}-1",
        "question" : f"From the camera's perspective, which object is located behind, the {parts[1]} ball or the {parts[2]} ball?",
        "A" : f"{parts[2]}",
        "B" : f"{parts[1]}",
        "C" : "",
        "D" : "",
        "answer" : "B" if angle_token in ("350", "0", "10", "330", "30") else "A",
        "category" : "front_behind",
        "image" : img_b64
    }

########## front_behind _flip
    
    # --- CHANGED: flip 이미지를 실제 저장/사용
    flip_path = ensure_flipped_image(img_path)          # (신규 저장 또는 재사용)
    img_b64 = encode_image_to_base64(flip_path)
    dict_infrontof_flip = {
#        "index" : i,
        "qid" : f"{qid_list1[i]}-flip",
        "question": f"From the camera's perspective, which object is located behind, the {parts[1]} ball or the {parts[2]} ball?",
        "A" : f"{parts[1]}",
        "B" : f"{parts[2]}",
        "C" : "",
        "D" : "",
        "answer" : "A" if angle_token in ("350", "0", "10", "330", "30") else "B",
        "category" : "front_behind",
        "image" : img_b64
    }
    dict_infrontof_flip_circ = {
#        "index" : i,
        "qid" : f"{qid_list1[i]}-flip-1",
        "question" : f"From the camera's perspective, which object is located behind, the {parts[1]} ball or the {parts[2]} ball?",
        "A" : f"{parts[2]}",
        "B" : f"{parts[1]}",
        "C" : "",
        "D" : "",
        "answer" : "B" if angle_token in ("350", "0", "10", "330", "30") else "A",
        "category" : "front_behind",
        "image" : img_b64
    }

    rows.append(dict_infrontof)
    rows.append(dict_infrontof_circ)
    rows.append(dict_infrontof_flip)
    rows.append(dict_infrontof_flip_circ)


############ closer

for i, img in enumerate(imgs_closer):
    img_path = os.path.join(img_dir1, img)

    # 1. 확장자 제거
    name_without_ext = img.rsplit(".", 1)[0]

    # 2. "_" 기준으로 분리
    parts = name_without_ext.split("_")
    print(parts)

    #0000_green_red_350.0
    
    img_b64 = encode_image_to_base64(img_path)
    angle_token = parts[-1].split(".")[0]

    # closer
    dict_closer = {
#        "index" : i,
        "qid" : qid_list2[i],
        "question": f"From the camera's perspective, which object is closer to the camera, the {parts[1]} ball or the {parts[2]} ball?",
        "A" : f"{parts[1]}",
        "B" : f"{parts[2]}",
        "C" : "",
        "D" : "",
        "answer" : "B" if angle_token in ("350", "0", "10", "330", "30") else "A",
        "category" : "closer",
        "image" : img_b64
    }

    # closer
    dict_closer_circ = {
#        "index" : i,
        "qid" : f"{qid_list2[i]}-1",
        "question": f"From the camera's perspective, which object is closer to the camera, the {parts[1]} ball or the {parts[2]} ball?",
        "A" : f"{parts[2]}",
        "B" : f"{parts[1]}",
        "C" : "",
        "D" : "",
        "answer" : "A" if angle_token in ("350", "0", "10", "330", "30") else "B",
        "category" : "closer",
        "image" : img_b64
    }


############ closer_flip
    
    # --- CHANGED: flip 이미지를 실제 저장/사용
    flip_path = ensure_flipped_image(img_path)
    img_b64 = encode_image_to_base64(flip_path)

    # closer
    dict_closer_flip = {
#        "index" : i,
        "qid" : f"{qid_list2[i]}-flip",
        "question": f"From the camera's perspective, which object is closer to the camera, the {parts[1]} ball or the {parts[2]} ball?",
        "A" : f"{parts[1]}",
        "B" : f"{parts[2]}",
        "C" : "",
        "D" : "",
        "answer" : "B" if angle_token in ("350", "0", "10", "330", "30") else "A",
        "category" : "closer",
        "image" : img_b64
    }

    # closer
    dict_closer_flip_circ = {
#        "index" : i,
        "qid" : f"{qid_list2[i]}-flip-1",
        "question": f"From the camera's perspective, which object is closer to the camera, the {parts[1]} ball or the {parts[2]} ball?",
        "A" : f"{parts[2]}",
        "B" : f"{parts[1]}",
        "C" : "",
        "D" : "",
        "answer" : "A" if angle_token in ("350", "0", "10", "330", "30") else "B",
        "category" : "closer",
        "image" : img_b64
    }


    rows.append(dict_closer)
    rows.append(dict_closer_circ)
    rows.append(dict_closer_flip)
    rows.append(dict_closer_flip_circ)




########### left, right
for i, img in enumerate(imgs2):
    img_path = os.path.join(img_dir2, img)

    # 1. 확장자 제거
    name_without_ext = img.rsplit(".", 1)[0]

    # 2. "_" 기준으로 분리
    parts = name_without_ext.split("_")

    parts = ['woman' if p == 'sophia' else p for p in parts]
    print(parts)

    #0000_green_red_chair_left_350.0
    
    img_b64 = encode_image_to_base64(img_path)
    angle_token = parts[-1].split(".")[0]

    # with addressee
    dict_lr = {
#        "index" : i,
        "qid" : qid_list3[i],
        "question": f"From the {parts[-3]}'s perspective, which object is located on the left side, the {parts[1]} ball or the {parts[2]} ball?",
        #             From the cat’s perspective, which object is located on the left side, the camel or the chair?
        "A" : f"{parts[1]}",
        "B" : f"{parts[2]}",
        "C" : "",
        "D" : "",
        "answer": (
            "A" if parts[-2] == "left"  and angle_token in ("350", "0", "10") else
            "B" if parts[-2] == "left"  and angle_token in ("170", "180", "190") else
            "B" if parts[-2] == "right" and angle_token in ("350", "0", "10") else
            "A" if parts[-2] == "right" and angle_token in ("170", "180", "190") else
            ""
        ),
        "category" : "left_right",
        "image" : img_b64
    }

    dict_lr_circ = {
#        "index" : i,
        "qid" : f"{qid_list3[i]}-1",
        "question": f"From the {parts[-3]}'s perspective, which object is located on the left side, the {parts[1]} ball or the {parts[2]} ball?",
        #             From the cat’s perspective, which object is located on the left side, the camel or the chair?
        "A" : f"{parts[2]}",
        "B" : f"{parts[1]}",
        "C" : "",
        "D" : "",
        "answer": (
            "B" if parts[-2] == "left"  and angle_token in ("350", "0", "10") else
            "A" if parts[-2] == "left"  and angle_token in ("170", "180", "190") else
            "A" if parts[-2] == "right" and angle_token in ("350", "0", "10") else
            "B" if parts[-2] == "right" and angle_token in ("170", "180", "190") else
            ""
        ),
        "category" : "left_right",
        "image" : img_b64,
    }




######### left_right_flip

    #0000_green_red_chair_left_350.0
    
    # --- CHANGED: flip 이미지를 실제 저장/사용
    flip_path = ensure_flipped_image(img_path)
    img_b64 = encode_image_to_base64(flip_path)

    # with addressee
    dict_lr_flip = {
#        "index" : i,
        "qid" : f"{qid_list3[i]}-flip",
        "question": f"From the {parts[-3]}'s perspective, which object is located on the left side, the {parts[1]} ball or the {parts[2]} ball?",
        #             From the cat’s perspective, which object is located on the left side, the camel or the chair?
        "A" : f"{parts[1]}",
        "B" : f"{parts[2]}",
        "C" : "",
        "D" : "",
        "answer": (
            "B" if parts[-2] == "left"  and angle_token in ("350", "0", "10") else
            "A" if parts[-2] == "left"  and angle_token in ("170", "180", "190") else
            "A" if parts[-2] == "right" and angle_token in ("350", "0", "10") else
            "B" if parts[-2] == "right" and angle_token in ("170", "180", "190") else
            ""
        ),
        "category" : "left_right",
        "image" : img_b64
    }

    dict_lr_flip_circ = {
#        "index" : i,
        "qid" : f"{qid_list3[i]}-flip-1",
        "question": f"From the {parts[-3]}'s perspective, which object is located on the left side, the {parts[1]} ball or the {parts[2]} ball?",
        #             From the cat’s perspective, which object is located on the left side, the camel or the chair?
        "A" : f"{parts[2]}",
        "B" : f"{parts[1]}",
        "C" : "",
        "D" : "",
        "answer": (
            "A" if parts[-2] == "left"  and angle_token in ("350", "0", "10") else
            "B" if parts[-2] == "left"  and angle_token in ("170", "180", "190") else
            "B" if parts[-2] == "right" and angle_token in ("350", "0", "10") else
            "A" if parts[-2] == "right" and angle_token in ("170", "180", "190") else
            ""
        ),
        "category" : "left_right",
        "image" : img_b64,
    }
    
    rows.append(dict_lr)
    rows.append(dict_lr_circ)
    rows.append(dict_lr_flip)
    rows.append(dict_lr_flip_circ)








for idx, rec in enumerate(rows):
    rec["index"] = idx

with open(output_tsv, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows)

"""
with open(output_tsv_aug, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields, delimiter="\t")
    writer.writeheader()
    writer.writerows(rows_aug)
"""