from dataclasses import dataclass, field
import numpy as np


@dataclass
class pmxpyTypeLoadVertex():
    ver: tuple[float, float, float] = field(init=False)
    nor: tuple[float, float, float] = field(init=False)
    uv: tuple[float, float] = field(init=False)
    add_uv: list[float] = field(init=False)
    weight_calc: int = field(init=False)
    sdef_options: list[float] = field(init=False)  # 3 * 3 + 1
    bone_id: list[int] = field(init=False)
    bone_weight: list[float] = field(init=False)
    edge: int = field(init=False)


@dataclass
class pmxpyTypeLoadMaterial():
    name: str = field(init=False)
    name_eng: str = field(init=False)
    diffuse: tuple[float, float, float, float] = field(init=False)
    specular_color: tuple[float, float, float] = field(init=False)
    specular_scale: float = field(init=False)
    ambient_color: tuple[float, float, float] = field(init=False)
    bit_flag: int = field(init=False)
    edge_color: tuple[float, float, float, float] = field(init=False)
    edge_size: float = field(init=False)
    texture_index: int = field(init=False)
    sphere_texture_index: int = field(init=False)
    sphere_mode: int = field(init=False)
    toon_flag: bool = field(init=False)
    texrure_name: str = field(init=False)
    toon_texture_number: int = field(init=False)
    comment: str = field(init=False)
    face_vert_count: int = field(init=False)


@dataclass
class pmxpyTypeLoadIKLink():
    bone_id: int = field(init=False)
    rotate_limit_flag: bool = field(init=False)
    btm: tuple[float, float, float] = field(init=False)
    top: tuple[float, float, float] = field(init=False)


@dataclass
class pmxpyTypeLoadIK():
    target_bone_index: int = field(init=False)
    iteration: int = field(init=False)
    radius_range: float = field(init=False)
    length: int = field(init=False)
    weight: float = field(init=False)
    child_bone_id: list[pmxpyTypeLoadIKLink] = field(init=False)


@dataclass
class pmxpyTypeLoadBone():
    name: str = field(init=False)
    name_eng: str = field(init=False)
    position: tuple[float, float, float] = field(init=False)
    parent_id: int = field(init=False)
    level: int = field(init=False)
    bone_flag: int = field(init=False)
    child_flag: bool = field(init=False)
    child_index: int = field(init=False)
    offset_position: tuple[float, float, float] = field(init=False)

    rotation_flag: bool = field(init=False)  # 回転可能
    translate_flag: bool = field(init=False)  # 移動可能
    show_flag: bool = field(init=False)  # 表示
    user_update_flag: bool = field(init=False)  # ユーザ操作可能

    # 回転付与
    grant_rotation_flag: bool = field(init=False)
    grant_rotation_index: int = field(init=False)
    grant_rotation_rate: float = field(init=False)

    # 移動付与
    grant_translate_flag: bool = field(init=False)
    grant_translate_index: int = field(init=False)
    grant_translate_rate: float = field(init=False)

    # 軸固定
    axis_vector: None | tuple[float, float, float] = field(init=False)

    # ローカル軸
    local_axis_flag: bool = field(init=False)
    local_axis_x: tuple[float, float, float] = field(init=False)
    local_axis_z: tuple[float, float, float] = field(init=False)

    # 物理後変形
    physical_update_flag: bool = field(init=False)

    # 外部親変形
    outside_parent_update_flag: bool = field(init=False)
    outside_parent_update_key_value: int = field(init=False)

    # IK
    ik: pmxpyTypeLoadIK | None = field(default=None)


# モーフ
@dataclass
class pmxpyTypeLoadMorphVertex():
    vertex_id: int = field(init=False)
    vertex: tuple[float, float, float] = field(init=False)


@dataclass
class pmxpyTypeLoadMorphUV():
    uv_number: int = field(init=False)
    uv_id: int = field(init=False)
    uv: tuple[float, float, float, float] = field(init=False)


@dataclass
class pmxpyTypeLoadMorphBone():
    bone_id: int = field(init=False)
    translate: tuple[float, float, float] = field(init=False)
    rotation: tuple[float, float, float, float] = field(init=False)


@dataclass
class pmxpyTypeLoadMorphMaterial():
    material_id: int = field(init=False)
    calc_format: int = field(init=False)
    diffuse: tuple[float, float, float, float] = field(init=False)
    specular: tuple[float, float, float] = field(init=False)
    specular_alpha: float = field(init=False)
    ambient: tuple[float, float, float] = field(init=False)
    edge_color: tuple[float, float, float, float] = field(init=False)
    edge_size: float = field(init=False)
    texture_alpha: tuple[float, float, float, float] = field(init=False)
    sphere_alpha: tuple[float, float, float, float] = field(init=False)
    toon_texture_alpha: tuple[float, float, float, float] = field(init=False)


@dataclass
class pmxpyTypeLoadMorphGroup():
    grouo_id: int = field(init=False)
    morph_rate: float = field(init=False)


@dataclass
class pmxpyTypeLoadMorph():
    name: str = field(init=False)
    eng_name: str = field(init=False)
    panel: int = field(init=False)
    type: int = field(init=False)
    offset_num: int = field(init=False)

    vertex: list[pmxpyTypeLoadMorphVertex] = field(init=False)
    uv: list[pmxpyTypeLoadMorphUV] = field(init=False)
    bone: list[pmxpyTypeLoadMorphBone] = field(init=False)
    material: list[pmxpyTypeLoadMorphMaterial] = field(init=False)
    group: list[pmxpyTypeLoadMorphGroup] = field(init=False)

    morph_flag: int = field(init=False)
    morph_step: float = field(init=False)
    sjis_name: str = field(init=False)


# 表示枠
@dataclass
class pmxpyTypeLoadDispFrameInline():
    type: int = field(init=False)
    index: int = field(init=False)


@dataclass
class pmxpyTypeLoadDispFrame():
    name: str = field(init=False)
    eng_name: str = field(init=False)
    frame_flag: int = field(init=False)

    index_num: int = field(init=False)
    indexs: list[pmxpyTypeLoadDispFrameInline] = field(init=False)


@dataclass
class pmxpyTypeLoadPhysicsBody():
    name: str = field(init=False)
    eng_name: str = field(init=False)

    bone_id: int = field(init=False)
    group_id: int = field(init=False)
    not_touch_group_flag: str = field(init=False)

    type_id: int = field(init=False)
    sizes: np.ndarray = field(init=False)

    pos: np.ndarray = field(init=False)
    rot: np.ndarray = field(init=False)

    mass: float = field(init=False)
    ac_t: float = field(init=False)
    ac_r: float = field(init=False)

    repulsion: float = field(init=False)
    friction: float = field(init=False)
    rigidbody_type: int = field(init=False)


@dataclass
class pmxpyTypeLoadPhysicsJoint():
    name: str = field(init=False)
    eng_name: str = field(init=False)

    type: int = field(init=False)

    a_index: int = field(init=False)
    b_index: int = field(init=False)

    pos: np.ndarray = field(init=False)
    rot: np.ndarray = field(init=False)

    trans_limit1: np.ndarray = field(init=False)
    trans_limit2: np.ndarray = field(init=False)

    rot_limit1: np.ndarray = field(init=False)
    rot_limit2: np.ndarray = field(init=False)

    spring_pos: np.ndarray = field(init=False)
    spring_rot: np.ndarray = field(init=False)


@dataclass
class pmdpyLoadPhysics():
    body: list[pmxpyTypeLoadPhysicsBody] = field(init=False)
    joint: list[pmxpyTypeLoadPhysicsJoint] = field(init=False)


@dataclass
class pmxpyType():
    filename: str = field(default="")
    path: str = field(default="")
    ext: str = field(default="")
    directory: str = field(default="")

    version: str = field(default="")
    name: str = field(default="")
    name_eng: str = field(default="")
    comment: str = field(default="")
    comment_eng: str = field(default="")

    encode_type: str = field(default="utf-8")
    add_uv_flag: bool = field(default=False)

    # face bit range
    face_index_sizeof: int = field(default=4)

    # bone index bit range
    bone_index_sizeof: int = field(default=4)

    # Texture index bit range
    texture_index_sizeof: int = field(default=4)

    # material index bit range
    material_index_sizeof: int = field(default=4)

    # morph index bit range
    morph_index_sizeof: int = field(default=4)

    # rigidbody index bit range
    rigidbody_index_sizeof: int = field(default=4)

    # load file struct
    vertex: list[pmxpyTypeLoadVertex] = field(init=False)
    face: list[tuple[int, int, int]] = field(init=False)
    texture_name: list[str] = field(init=False)
    material: list[pmxpyTypeLoadMaterial] = field(init=False)
    bone: list[pmxpyTypeLoadBone] = field(init=False)
    morph: list[pmxpyTypeLoadMorph] = field(init=False)
    disp: list[pmxpyTypeLoadDispFrame] = field(init=False)

    physics_flag: bool = field(init=False)

    physics: None | pmdpyLoadPhysics = field(init=False)
