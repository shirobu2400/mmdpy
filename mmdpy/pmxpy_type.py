from typing import Union, Any, List, Tuple, Dict
from dataclasses import dataclass, field


@dataclass
class pmxpyTypeLoadVertex():
    ver: Tuple[float, float, float] = field(init=False)
    nor: Tuple[float, float, float] = field(init=False)
    uv: Tuple[float, float] = field(init=False)
    add_uv: List[float] = field(init=False)
    weight_calc: int = field(init=False)
    sdef_options: List[float] = field(init=False)  # 3 * 3 + 1
    bone_id: List[int] = field(init=False)
    bone_weight: List[float] = field(init=False)
    edge: int = field(init=False)


@dataclass
class pmxpyTypeLoadMaterial():
    name: str = field(init=False)
    name_eng: str = field(init=False)
    diffuse: Tuple[float, float, float, float] = field(init=False)
    specular_color: Tuple[float, float, float] = field(init=False)
    specular_scale: float = field(init=False)
    ambient_color: Tuple[float, float, float] = field(init=False)
    bit_flag: int = field(init=False)
    edge_color: Tuple[float, float, float, float] = field(init=False)
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
    btm: Tuple[float, float, float] = field(init=False)
    top: Tuple[float, float, float] = field(init=False)


@dataclass
class pmxpyTypeLoadIK():
    target_bone_index: int = field(init=False)
    iteration: int = field(init=False)
    radius_range: float = field(init=False)
    length: int = field(init=False)
    weight: float = field(init=False)
    child_bone_id: List[pmxpyTypeLoadIKLink] = field(init=False)


@dataclass
class pmxpyTypeLoadBone():
    name: str = field(init=False)
    name_eng: str = field(init=False)
    position: Tuple[float, float, float] = field(init=False)
    parent_id: int = field(init=False)
    level: int = field(init=False)
    bone_flag: int = field(init=False)
    child_flag: bool = field(init=False)
    child_index: int = field(init=False)
    offset_position: Tuple[float, float, float] = field(init=False)

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
    axis_vector: Union[None, Tuple[float, float, float]] = field(init=False)

    # ローカル軸
    local_axis_flag: bool = field(init=False)
    local_axis_x: Tuple[float, float, float] = field(init=False)
    local_axis_z: Tuple[float, float, float] = field(init=False)

    # 物理後変形
    physical_update_flag: bool = field(init=False)

    # 外部親変形
    outside_parent_update_flag: bool = field(init=False)
    outside_parent_update_key_value: int = field(init=False)

    # IK
    ik: Union[pmxpyTypeLoadIK, None] = field(default=None)


@dataclass
class pmdpyTypeLoadSkin():
    name: str = field(init=False)
    var_size: int = field(init=False)
    type: int = field(init=False)
    var_id: List[int] = field(init=False)
    ver_offset: List[Tuple[float, float, float]] = field(init=False)


@dataclass
class pmdpyTypeLoadBoneName():
    id: int = field(init=False)
    frame: int = field(init=False)


@dataclass
class pmdpyTypeLoadPhysicsBodyVector():
    x: float = field(init=False)
    y: float = field(init=False)
    z: float = field(init=False)


@dataclass
class pmdpyTypeLoadPhysicsBody():
    name: str = field(init=False)
    bone_id: int = field(init=False)
    group_id: int = field(init=False)
    group_mask: str = field(init=False)
    type_id: int = field(init=False)
    sizes: pmdpyTypeLoadPhysicsBodyVector = field(init=False)
    pos: Tuple[Any, ...] = field(init=False)
    rot: Tuple[Any, ...] = field(init=False)
    mass: float = field(init=False)
    pos_dim: float = field(init=False)
    rot_dim: float = field(init=False)
    recoil: float = field(init=False)
    friction: float = field(init=False)
    calc: int = field(init=False)


@dataclass
class pmdpyTypeLoadPhysicsJoint():
    name: str = field(init=False)
    rigidbody_a: int = field(init=False)
    rigidbody_b: int = field(init=False)
    pos: Tuple[Any, ...] = field(init=False)
    rot: Tuple[Any, ...] = field(init=False)
    constrain_pos: List[Tuple[Any, ...]] = field(init=False)
    spring_pos: Tuple[Any, ...] = field(init=False)
    spring_rot: Tuple[Any, ...] = field(init=False)


@dataclass
class pmdpyLoadPhysics():
    body: List[pmdpyTypeLoadPhysicsBody] = field(init=False)
    joint: List[pmdpyTypeLoadPhysicsJoint] = field(init=False)


@dataclass
class pmdpyTypeAdjustVertex():
    ver: Tuple[Any, ...] = field(init=False)
    nor: Tuple[Any, ...] = field(init=False)
    uv: Tuple[Any, ...] = field(init=False)
    bone_id: Tuple[Any, ...] = field(init=False)
    bone_weight: Tuple[Any, ...] = field(init=False)
    edge: int = field(init=False)


@dataclass
class pmdpyTypeBone():
    bone_me: Union[Any, int] = field(init=False)
    bone_to: Union[Any, int] = field(init=False)
    len: int = field(init=False)
    iteration: int = field(init=False)
    weight: Any = field(init=False)
    child_bones: Any = field(init=False)
    ik: Any = field(init=False)


@dataclass
class pmdpyTypeAdjustIK():
    bone_me: Union[Any, int] = field(init=False)
    bone_to: Union[Any, int] = field(init=False)
    len: int = field(init=False)
    iteration: int = field(init=False)
    weight: Any = field(init=False)
    child_bones: Any = field(init=False)
    ik: Any = field(init=False)


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

    # load file struct
    vertex: List[pmxpyTypeLoadVertex] = field(init=False)
    face: List[Tuple[int, int, int]] = field(init=False)
    texture_name: List[str] = field(init=False)
    material: List[pmxpyTypeLoadMaterial] = field(init=False)
    bone: List[pmxpyTypeLoadBone] = field(init=False)
    skin: List[pmdpyTypeLoadSkin] = field(init=False)
    skin_name: List[int] = field(init=False)
    bone_frame_name: List[str] = field(init=False)
    bone_number: List[pmdpyTypeLoadBoneName] = field(init=False)

    english_flag: bool = field(init=False)
    english_head: Dict[str, str] = field(init=False)
    bone_name_eng: List[str] = field(init=False)
    skin_name_eng: List[str] = field(init=False)
    bone_disp_name_eng: List[str] = field(init=False)

    toon_name: List[str] = field(init=False)
    physics_flag: bool = field(init=False)
    physics: Union[None, pmdpyLoadPhysics] = field(init=False)
