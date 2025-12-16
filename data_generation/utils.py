
import os
import re
import sys
import bpy
import cv2
import math
import copy
import json
import random
import numpy as np
from mathutils import Vector
from typing import Union, List, Dict

from data_generation.comfort_ball_config import *
from data_generation.constants import *


def get_rotation_path(var_obj, radius, angle_range, num_steps):
    start_angle, end_angle = angle_range
    angle_step = (end_angle - start_angle) / (num_steps-1) # 원 궤적 균등 분할

    var_obj_path = []
    for step in range(num_steps):
        angle = math.radians(start_angle + step * angle_step)
        var_obj.location = ( # 각 step에서의 위치
            radius * math.cos(angle),
            radius * math.sin(angle),
            var_obj.location.z,
        )
        angle = step * angle_step - 180
        var_obj_path.append((list(var_obj.location.copy()), angle))

    return var_obj_path # return location, angle 


def add_distractor_objects(ref_shape, var_shape, ref_color, var_color, num_distractors, ref_obj, var_obj, var_obj_path, ref_obj_path=None, distractors=None, comfort_ball=True):
    # Collect existing positions and dimensions from the ref_obj and var_obj
    existing_positions = [
        (ref_obj.location.copy(), ref_obj.dimensions.copy()),
        (var_obj.location.copy(), var_obj.dimensions.copy())
    ]

    # Add positions from var_obj's path to the list
    for entry in var_obj_path:
        if isinstance(entry, tuple):
            position = entry[0]  # Assuming the first element is the position if it's a tuple
        else:
            position = entry  # Directly use the entry if it's already a position
        existing_positions.append((position, var_obj.dimensions.copy()))

    if ref_obj_path is not None:
        for entry in ref_obj_path:
            existing_positions.append((entry, ref_obj.dimensions.copy()))

    if distractors is not None:
        for distractor in distractors:
            existing_positions.append((distractor['location'], distractor['dimensions']))
            distractor_obj = add_object(
                    SHAPE_DIR,
                    distractor['shape'],
                    distractor['size'],
                    distractor['position'],
                    comfort_ball=comfort_ball
                )
            distractor_color = distractor['color']
            distractor_mat = bpy.data.materials.new(name="DistractorMaterial")
            distractor_mat.use_nodes = True
            distractor_bsdf_node = distractor_mat.node_tree.nodes.get("Principled BSDF")
            distractor_bsdf_node.inputs["Base Color"].default_value = distractor_color
            distractor_obj.data.materials.append(distractor_mat)

    excluded_shapes = {ref_shape, var_shape}
    excluded_colors = {ref_color, var_color}

    # Now add distractors
    iter = num_distractors if distractors is None else num_distractors - len(distractors)
    for _ in range(iter):

        if comfort_ball:
            available_colors = [GREEN]
            available_shapes = [SPHERE]
    
        else:
            available_shapes = [BICYCLE_MOUNTAIN]
            available_colors = [CAR_BLUE]

        placed = False
        while not placed:
            distractor_shape = random.choice(available_shapes)

            if comfort_ball:
                # distractor_size = random.uniform(0.4, 0.7)
                distractor_size = 0.5
                distractor_position = (
                    random.uniform(0, 3.5),
                    random.uniform(-2.0, 2.0),
                    distractor_size,
                )
            else:
                # distractor_size = random.uniform(2.5,3)
                distractor_size = 2.0
                distractor_position = (
                    random.uniform(-2.5, 5.5),
                    random.uniform(-2.5, 2.5),
                    0.5,
                )

            # if distractor_shape not in AEROPLANES:
            #     continue

            # Check for collisions
            collision = False
            for position, dimensions in existing_positions:
                
                offset = dimensions[0] / 1.5 if comfort_ball else dimensions[0] / distractor_size / 2
                
                distractor_offset = distractor_size / 1.25 if not comfort_ball else distractor_size
                if (
                    abs(distractor_position[0] - position[0]) < (distractor_offset + offset) and
                    abs(distractor_position[1] - position[1]) < (distractor_offset + offset) and
                    abs(distractor_position[2] - position[2]) < (distractor_offset + offset)
                ):
                    collision = True
                    break
            
            if not collision:
                placed = True
                distractor_obj = add_object(
                    SHAPE_DIR,
                    distractor_shape,
                    distractor_size,
                    distractor_position,
                    comfort_ball=comfort_ball
                )
                distractor_color = random.choice(
                    available_colors
                )
                distractor_mat = bpy.data.materials.new(name="DistractorMaterial")
                distractor_mat.use_nodes = True
                distractor_bsdf_node = distractor_mat.node_tree.nodes.get("Principled BSDF")
                distractor_bsdf_node.inputs["Base Color"].default_value = distractor_color
                distractor_obj.data.materials.append(distractor_mat)
                existing_positions.append(
                    (distractor_obj.location, (distractor_size, distractor_size, distractor_size))
                )
                # Check if the object has multiple parts
                if distractor_obj.type == 'MESH':
                    for slot in distractor_obj.material_slots:
                        part_name = slot.name
                        # printing part names to not color the wheels or other parts
                        # print("Part name:", part_name, file=sys.stderr)
                        if "wheel" in part_name.lower():
                            slot.material.node_tree.nodes["Diffuse BSDF"].inputs['Color'].default_value = BLACK
                        else:
                            if slot.material.node_tree.nodes.get("Diffuse BSDF", None) is not None:
                                # print(slot.material.node_tree.nodes.keys(), file=sys.stderr)
                                slot.material.node_tree.nodes["Diffuse BSDF"].inputs['Color'].default_value = distractor_color


        if distractors is None:
            distractors = []
        distractors.append({'location': distractor_obj.location.copy(), 'dimensions': distractor_obj.dimensions.copy(), 'shape': distractor_shape, 'color': distractor_color, 'size': distractor_size, 'position': distractor_position})

        return distractors
    
def add_object(object_dir, name, scale, loc, theta=0, relation=None, comfort_ball=True):
    count = sum(1 for obj in bpy.data.objects if obj.name.startswith(name))

    # append 전에 존재하던 오브젝트 이름들
    before = set(bpy.data.objects.keys())

    if comfort_ball:
        filename = os.path.join(object_dir, f"{name}.blend", "Object", name)
    else:
        parts = str(name).split("_")
        object_basename = parts[1] if len(parts) >= 2 else parts[0]
        filename = os.path.join(object_dir, f"{name}.blend", "Object", object_basename)

    bpy.ops.wm.append(filename=filename)

    # append 이후 추가된 오브젝트를 정확히 집어낸다
    after = set(bpy.data.objects.keys())
    added = list(after - before)
    if not added:
        # fallback: 그래도 없으면 기존 키로 접근 (마지막 안전장치)
        added = [name] if name in bpy.data.objects else list(after)

    # 방금 추가된 오브젝트(첫 번째)로 확정
    src_key = added[0]
    new_name = f"{name}_{count}"
    bpy.data.objects[src_key].name = new_name

    # 이후는 기존대로 active/transform
    x, y, z = loc
    bpy.context.view_layer.objects.active = bpy.data.objects[new_name]
    bpy.context.object.rotation_euler[2] = theta
    bpy.ops.transform.resize(value=(scale, scale, scale))
    bpy.ops.transform.translate(value=(x, y, z))

    return bpy.context.object

def load_materials(material_dir):
    """
    Load materials from a directory. We assume that the directory contains .blend
    files with one material each. The file X.blend has a single NodeTree item named
    X; this NodeTree item must have a "Color" input that accepts an RGBA value.
    """
    for fn in os.listdir(material_dir):
        if not fn.endswith(".blend"):
            continue
        name = os.path.splitext(fn)[0]
        filepath = os.path.join(material_dir, fn, "NodeTree", name)
        bpy.ops.wm.append(filename=filepath)

def ensure_object_mode():
    if bpy.context.object:
        if bpy.context.object.mode != 'OBJECT':
            # Attempt to change to object mode
            bpy.ops.object.mode_set(mode='OBJECT')

def select_objects_for_join(objects):
    # Deselect all to start clean
    bpy.ops.object.select_all(action='DESELECT')

    # Ensure the context is correct by explicitly setting the active object
    for obj in objects:
        obj.select_set(True)
    
    # Set the first object as the active object
    bpy.context.view_layer.objects.active = objects[0] if objects else None

def join_objects(objects):
    # Select objects and ensure correct context
    select_objects_for_join(objects)

    # Perform the join operation
    bpy.ops.object.join()

def make_single_user(objects):
    for obj in objects:
        if obj.data and obj.data.users > 1:  # Check if data is shared
            obj.data = obj.data.copy()  # Make a single-user copy of the data


def create_and_setup_object(
        shape_dir, 
        shape, 
        size, 
        position, 
        material_name=None, 
        color=None, 
        relation=None, 
        comfort_ball=True
    ):
    # print("comfort_ball:", comfort_ball, file=sys.stderr)
    if not comfort_ball:
        if shape in SPECIAL:
            with bpy.data.libraries.load(os.path.join(shape_dir, f"{shape}.blend"), link=False) as (data_from, data_to):
                data_to.objects = data_from.objects
                # print("Objects loaded:", data_from.objects, file=sys.stderr)  # Debugging line
            # Link objects to the collection and apply transformations
        # Link objects to the collection
        # Ensure Blender is in object mode
            ensure_object_mode()
            make_single_user(data_to.objects)
            # Link objects to the scene
            for obj in data_to.objects:
                if obj is not None:
                    bpy.context.collection.objects.link(obj)

            # Try to join objects
            try:
                join_objects(data_to.objects)
                print("Objects successfully joined.")
            except RuntimeError as e:
                print(f"Failed to join objects: {e}")

            # Set position and optionally scale
            if data_to.objects:
                active_object = bpy.context.active_object
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                active_object.location = position
                # active_object.rotation
                # addressee_obj.rotation_euler = tuple(np.array(addressee_rotation) / 180. * math.pi)
                # active_object.rotation_euler = tuple(np.array([0, 0, 90]) / 180. * math.pi)
                # if size:
                #     # active_object.scale = size
                #     bpy.ops.object.transform_apply(scale=True)
            
            return bpy.context.active_object

        else:
            print("Creating object", shape, file=sys.stderr)
            obj = add_object(shape_dir, shape, size, position, relation=relation, comfort_ball=comfort_ball)
            print(obj.scale, file=sys.stderr)
        
        # print(obj, file=sys.stderr)
        # Set up the object's material and transformations
        # Ensure the object is of a type that supports materials, like 'MESH'
        if obj and obj.type == 'MESH':
            obj.data.use_auto_smooth = True
            if material_name is not None and color is not None:
                mat = bpy.data.materials.new(name=material_name)
                mat.use_nodes = True
                bsdf_node = mat.node_tree.nodes.get("Principled BSDF")
                bsdf_node.inputs["Base Color"].default_value = color
                obj.data.materials.append(mat)

            bpy.context.view_layer.objects.active = obj
            # bpy.context.object.rotation_euler[2] = 0  # Adjust if you need rotation
            bpy.ops.transform.resize(value=(size, size, size))
            bpy.ops.transform.translate(value=position)
        # Calculate offset to ground and set position
            obj_dimensions = obj.dimensions
            z_offset = obj_dimensions.z / 2  # Assuming the origin is at the center
            new_position = (position[0], position[1], position[2] - z_offset)
            bpy.ops.transform.translate(value=new_position)
            

            for slot in obj.material_slots:
                part_name = slot.name
                if "wheel" in part_name.lower():
                    slot.material.node_tree.nodes["Diffuse BSDF"].inputs['Color'].default_value = (0, 0, 0, 1)  # Assuming BLACK is defined
                else:
                    diff_bsdf = slot.material.node_tree.nodes.get("Diffuse BSDF", None)
                    if diff_bsdf:
                        diff_bsdf.inputs['Color'].default_value = color
        else:
            print("The imported or created object is not compatible with materials.")
    else:
        obj = add_object(shape_dir, shape, size, position, relation=relation, comfort_ball=comfort_ball)
        if material_name is not None and color is not None:

            mat = bpy.data.materials.new(name=material_name)
            mat.use_nodes = True
            bsdf_node = mat.node_tree.nodes.get("Principled BSDF")
            bsdf_node.inputs["Base Color"].default_value = color
            obj.data.materials.append(mat)

            # Check if the object has multiple parts
            if obj.type == 'MESH':
                for slot in obj.material_slots:
                    part_name = slot.name
                    # printing part names to not color the wheels or other parts
                    # print("Part name:", part_name, file=sys.stderr)
                    if "wheel" in part_name.lower():
                        slot.material.node_tree.nodes["Diffuse BSDF"].inputs['Color'].default_value = BLACK
                    else:
                        if slot.material.node_tree.nodes.get("Diffuse BSDF", None) is not None:
                            # print(slot.material.node_tree.nodes.keys(), file=sys.stderr)
                            slot.material.node_tree.nodes["Diffuse BSDF"].inputs['Color'].default_value = color

    return obj




def disable_shadow_completely(obj):
    # 1) 던지지 않기 (Cycles)
    if hasattr(obj, "cycles_visibility"):
        obj.cycles_visibility.shadow = False

    # 2) 받지 않기 (머티리얼 트릭: Eevee/Cycles 공통적으로 유용)
    for slot in obj.material_slots:
        mat = slot.material
        if not mat:
            continue
        mat.use_nodes = True
        # Eevee에선 아래가 직접적으로 먹힘 (Cycles에서도 부작용 없이 안전)
        if hasattr(mat, "shadow_method"):
            mat.shadow_method = 'NONE'   # 이 머티리얼은 그림자 관련 영향 배제

        # (선택) 완전한 “그림자 무시”를 위해 Light Path 노드로 Shadow Ray 차단
        nt = mat.node_tree
        nodes, links = nt.nodes, nt.links
        output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
        bsdf = nodes.get("Principled BSDF") or next((n for n in nodes if n.type.endswith("BSDF")), None)
        lp = nodes.new("ShaderNodeLightPath")
        transparent = nodes.new("ShaderNodeBsdfTransparent")
        mix = nodes.new("ShaderNodeMixShader")
        mix.inputs[0].default_value = 1.0  # 기본값 (Is Shadow Ray로 대체됨)
        links.new(lp.outputs["Is Shadow Ray"], mix.inputs[0])    # 그림자 광선이면
        links.new(transparent.outputs[0], mix.inputs[1])         # 투명으로
        if bsdf:
            links.new(bsdf.outputs[0], mix.inputs[2])            # 그 외엔 기존 BSDF
            links.new(mix.outputs[0], output.inputs[0])




def render_scene_config(
        variation: str,
        relation: str,
        path_type: str,
        num_steps: int,
        save_path: str,
        
        ref_shape: str,
        ref_color: tuple,
        ref_size: float,
        ref_position: tuple,
        ref_rotation: Union[tuple, List[tuple]],

        var_shape: str,
        var_color: tuple,
        var_size: float,
        var_position: tuple,
        var_rotation: tuple,
        start_point: tuple = None,
        end_point: tuple = None,

        cam_position_list: List[tuple] = None,  # ✅ 추가
        radius_list: List[float] = None,   # ✅ 추가

        radius: int = None,
        angle_range: tuple = None,
        angle_list: List[float] = None,
        var_size_list: List[float] = None,
        var_size_by_angle: Dict[float, float] = None,

        num_distractors: int = 0,
        cam_position: tuple = None,

        addressee: bool = False,
        addressee_shape: str = None,
        addressee_position: tuple = None,
        addressee_size: float = None,
        addressee_rotation: tuple = None,

        distractors: list = [],

        name: str = None,
        dataset_name: str = None,
        render_shadow: bool = False,
        cuda: bool = True,

        global_idx: int = 0,
        var_position_list: List[tuple] = None,

        ref_size_list: List[float] = None,         # ✅ 추가
        ref_position_list: List[tuple] = None,     # ✅ 추가
        cam_pitch_deg: float | None = None,   # ✅ 추가: 카메라 pitch(deg)
) -> dict:
    
    print({
    "IN_RENDER.addressee": addressee,
    "IN_RENDER.addr_shape": addressee_shape,
    "IN_RENDER.addr_pos": addressee_position,
    "IN_RENDER.addr_rot": addressee_rotation,

    }, file=sys.stderr, flush=True)


    bpy.context.scene.render.engine = "CYCLES"
    if True:
        preferences = bpy.context.preferences.addons['cycles'].preferences
        preferences.get_devices()

        if cuda:
            for device in preferences.devices:
                device.use = True
            preferences.compute_device_type = 'CUDA'
            bpy.context.scene.cycles.device = 'GPU'
    bpy.ops.wm.open_mainfile(filepath=BASE_SCENE)
    bpy.context.scene.render.resolution_x = IM_SIZE
    bpy.context.scene.render.resolution_y = IM_SIZE
    bpy.context.scene.render.resolution_percentage = 100


    if not render_shadow:
        # 1) 모든 오브젝트가 "shadow ray"에 보이지 않게 (그림자 생성 차단)
        for obj in bpy.data.objects:
            if hasattr(obj, "cycles_visibility"):
                obj.cycles_visibility.shadow = False
    # 라이트에서 그림자 제거
        for light in bpy.data.lights:
            if hasattr(light, "use_shadow"):
                light.use_shadow = False
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                obj.cycles.is_shadow_catcher = False
            # World 환경광에서 그림자/조명 차단
        if bpy.context.scene.world:
            bpy.context.scene.world.use_nodes = False

        for o in (ref_obj, var_obj):
            if hasattr(o, "cycles_visibility"):
                o.cycles_visibility.shadow = False 

    print(relation, file=sys.stderr)

    if dataset_name == "comfort_ball":
        comfort_ball = True
    else:
        comfort_ball = False


    # Disable shadow casting for all lights
    camera = bpy.data.objects['Camera']
    if comfort_ball:
        camera.location = (7.8342, 0, 5)
    else:
        camera.location = (14.0, 0, 7.0)

    if cam_position is not None:
        camera.location = cam_position

    # ✅ 최소 수정: 요청 시 pitch만 살짝 내려준다 (음수면 아래로 내려다봄)
 #   if cam_pitch_deg is not None:
        camera.rotation_euler[0] = math.radians(cam_pitch_deg)

    variation_name = variation
    SAVE_DIR = os.path.join(save_path, relation, variation_name)

    ##################파일 이름 만들기
    # ---- helpers: color->name, side ----
    COLOR_NAME_MAP = {
        tuple(RED): "red",
        tuple(BLUE): "blue",
        tuple(GREEN): "green",
        tuple(YELLOW): "yellow",
        tuple(PURPLE): "purple",
        tuple(ORANGE): "orange",
        tuple(CYAN): "cyan",
        tuple(GRAY): "gray",
        tuple(DARK_GRAY): "darkgray",
        tuple(WHITE): "white",
        tuple(AIRPLANE_WHITE): "airplane_white",
        tuple(CHARCOAL_GRAY): "charcoal_gray",
        tuple(CAR_RED): "car_red",
        tuple(CAR_BLUE): "car_blue",
        tuple(BLACK): "black"
    }

    def color_to_name(c):
        # constants의 색 튜플이 그대로 들어온다는 가정 (RGBA 4원소)
        # 만약 float 오차 가능성이 있으면 round/epsilon 비교를 추가
        return COLOR_NAME_MAP.get(tuple(c), "unknown")

    def side_from_position(pos):
        if not pos:
            return None
        x = pos[1]
        if x < 0: return "left"
        if x > 0: return "right"
        return "center"

    # ---- base filename (directory 유지, 파일명만 커스텀) ----
    ref_col_name = color_to_name(ref_color)
    var_col_name = color_to_name(var_color)

    parts = [ref_col_name, var_col_name]

    if addressee:
        add_name = str(addressee_shape).lower() if addressee_shape else "addressee"
        side = side_from_position(addressee_position)
        if side:
            parts += [add_name, side]
        else:
            parts += [add_name]

    base_filename = "_".join(parts)  # 예: "blue_red_sophia_left"
    #################################


    mapping = {}

    if dataset_name == "comfort_ball":
        comfort_ball = True
    else:
        comfort_ball = False

    if path_type == "rotate":
        # addressee object
        if addressee:
            addressee_obj = create_and_setup_object(
                SHAPE_DIR, 
                addressee_shape, 
                addressee_size, 
                addressee_position,
                "AddMaterial",
                None,
                relation = None,
                comfort_ball=False
            )
            
            if addressee_shape in SPECIAL:
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
                bpy.context.view_layer.objects.active = addressee_obj
                addressee_obj.rotation_euler = tuple(np.array(addressee_rotation) / 180. * math.pi)
            addressee_obj.scale = (addressee_size, addressee_size, addressee_size)
            bpy.ops.object.transform_apply(scale=True)
        #print({
        #    "ADDRESSEE": True,
        #    "name": addressee_obj.name,
        #    "loc": tuple(addressee_obj.location),
        #    "rot": tuple(addressee_obj.rotation_euler),
        #    "dims": tuple(addressee_obj.dimensions),
        #}, file=sys.stderr)


        # reference object
        ref_obj = create_and_setup_object(
            SHAPE_DIR, 
            ref_shape, 
            ref_size, 
            ref_position, 
            "RefMaterial", 
            ref_color, 
            relation=None,
            comfort_ball=comfort_ball
        )


                # ✅ ref를 바라보도록 정렬 (한 번만)
        direction = Vector(ref_obj.location) - camera.location
        camera.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

        # ✅ 추가 원하는 만큼 더 숙이기 (옵션)
        if cam_pitch_deg is not None:
            camera.rotation_euler[0] += math.radians(cam_pitch_deg)


        if ref_shape in SPECIAL:
            bpy.context.view_layer.objects.active = ref_obj
            ref_obj.rotation_euler = tuple(np.array(ref_rotation) / 180. * math.pi)
            if ref_shape == BED:
                ref_obj.scale = (ref_size, ref_size, ref_size*1/2)
            else:
                ref_obj.scale = (ref_size, ref_size, ref_size)
            bpy.ops.object.transform_apply(rotation=True, scale=True)
        else:
            ref_obj.rotation_euler = tuple(np.array(ref_rotation) / 180. * math.pi)



        # target object
        var_obj = create_and_setup_object(
            SHAPE_DIR, 
            var_shape, 
            var_size, 
            var_position, 
            "VarMaterial", 
            var_color, 
            relation=None,
            comfort_ball=comfort_ball
        )

    #    disable_shadow_completely(ref_obj)
    #    disable_shadow_completely(var_obj)


        if var_shape in SPECIAL:
            var_obj.rotation_euler = tuple(np.array(var_rotation) / 180. * math.pi)
            bpy.context.view_layer.objects.active = var_obj
            var_obj.scale = (var_size, var_size, var_size)
            bpy.ops.object.transform_apply(scale=True)
        else:
            var_obj.rotation_euler = tuple(np.array(var_rotation) / 180. * math.pi)
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
        # 여기서 '각도 리스트'가 있으면 그걸로 경로를 만들고,
        # 없으면 기존 get_rotation_path(...)를 그대로 사용
        if angle_list and len(angle_list) > 0:
            # 안전 정규화
            angles_deg = [float(a) % 360.0 for a in angle_list]

            # rotate 경로인데 radius가 None이면 기본값 보정 (필요 시 조정)
            if radius is None:
                radius = 2.9

            # ref_obj의 현재 location을 중심으로 원궤도 좌표 생성
            cx, cy, cz = ref_obj.location
            var_z = var_obj.location.z  # 높이는 기존 var 위치의 z를 유지(원하면 cz로 교체)

            var_obj_path = []
            for i, a_deg in enumerate(angles_deg):
                ang = math.radians(a_deg)
                # 좌표계에 맞춰 cos/sin 축을 바꾸고 싶으면 여기 수정
                # ✅ step별 radius 적용
                r = radius_list[i] if (radius_list is not None and i < len(radius_list)) else radius
                x = cx + r * math.cos(ang)
                y = cy + r * math.sin(ang)
                pos = (x, y, var_z)
                var_obj_path.append((pos, a_deg))
            # num_steps도 angle_list 길이에 맞춰 덮어쓸 수 있음 (원한다면)
            # num_steps = len(angles_deg)
        else:
            # 기존 get_rotation_path 대신 step별 radius 적용
            start_angle, end_angle = angle_range
            angle_step = (end_angle - start_angle) / (num_steps - 1)
            var_obj_path = []
            for step in range(num_steps):
                ang = math.radians(start_angle + step * angle_step)
                # ✅ step별 radius 적용
                r = radius_list[step] if (radius_list is not None and step < len(radius_list)) else radius
                x = r * math.cos(ang)
                y = r * math.sin(ang)
                pos = (x, y, var_obj.location.z)
                angle = step * angle_step - 180
                var_obj_path.append((pos, angle))
            angles_deg = [float(ang) % 360.0 for _, ang in var_obj_path]






            # 기존 방식 유지
#            var_obj_path = get_rotation_path(var_obj, radius, angle_range, num_steps)
            # get_rotation_path가 (pos, angle) 형태를 주므로 각도 리스트를 재구성
#            angles_deg = [float(ang) % 360.0 for _, ang in var_obj_path]
        # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

        added_distractors = add_distractor_objects(
            ref_shape, 
            var_shape, 
            ref_color, 
            var_color, 
            num_distractors, 
            ref_obj, 
            var_obj, 
            var_obj_path, 
            distractors=distractors, 
            comfort_ball=comfort_ball
        )

        # ========= [여기에 '각 step별 size 결정' 블록을 넣는다] =========
        if var_size_list and len(var_size_list) == len(angles_deg):
            sizes_per_step = list(var_size_list)
        else:
            sizes_per_step = [var_size] * len(angles_deg)

        # ✅ ref: 새로 추가 (var와 동일한 방식)
        if ref_size_list and len(ref_size_list) == len(angles_deg):
            ref_sizes_per_step = list(ref_size_list)
        else:
            ref_sizes_per_step = [ref_size] * len(angles_deg)
        # ============================================================
        





        cur_idx = global_idx
        bpy.context.scene.render.image_settings.file_format = 'JPEG'

        for i, (pos, angle) in enumerate(var_obj_path):
            # per-step 크기 적용
            step_size = sizes_per_step[i]
            var_obj.scale = (step_size, step_size, step_size)    

            if cam_position_list is not None and i < len(cam_position_list):
                camera.location = cam_position_list[i]


            z_val = var_position_list[i][2]
            new_pos = (pos[0], pos[1], z_val)
            var_obj.location = new_pos


            # --- ✅ ref per-step (ball 가정, 최소 수정) ---
            ref_step_size = ref_sizes_per_step[i]                     # ① 크기 선택
            ref_obj.scale = (ref_step_size, ref_step_size, ref_step_size)  # ② 스케일 적용
            ref_z = (ref_position_list[i][2] if ref_position_list else ref_step_size)  # ③ z=리스트 있으면 그 값, 없으면 크기
            ref_obj.location = (ref_obj.location.x, ref_obj.location.y, ref_z)



            filename = f"{cur_idx:04d}_{base_filename}_{angle}.jpg"
            
            output_image = os.path.join(SAVE_DIR, filename)
            bpy.context.scene.render.filepath = output_image
            bpy.ops.render.render(write_still=True)
            print(f"Rendered image path: {output_image}", file=sys.stderr)
            # print(f"Angle: {angle}", file=sys.stderr)
            mapping[os.path.basename(filename)] = int(angle)
            cur_idx += 1


    return mapping, added_distractors, cur_idx