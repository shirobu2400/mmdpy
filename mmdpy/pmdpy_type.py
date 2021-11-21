from typing import Union, Any, List, Tuple, Dict
from dataclasses import dataclass, field


@dataclass
class pmdpyTypeLoadVertex():
    ver: Tuple[float, float, float] = field(init=False)
    nor: Tuple[float, float, float] = field(init=False)
    uv: Tuple[float, float] = field(init=False)
    bone_id: Tuple[int, int] = field(init=False)
    bone_weight: Tuple[float, float] = field(init=False)
    edge: int = field(init=False)


@dataclass
class pmdpyTypeLoadMaterial():
    diffuse: Tuple[float, float, float] = field(init=False)
    alpha: float = field(init=False)
    specularity: Tuple[float, float, float] = field(init=False)
    specular_color: Tuple[float, float, float] = field(init=False)
    mirror_color: Tuple[float, float, float] = field(init=False)
    toon_index: int = field(init=False)
    edge: bool = field(init=False)
    face_vert_count: int = field(init=False)
    texture_name: bytes = field(init=False)


@dataclass
class pmdpyTypeLoadBone():
    name: str = field(init=False)
    parent_id: int = field(init=False)
    tail_id: int = field(init=False)
    bone_type: int = field(init=False)
    ik_parent_id: int = field(init=False)
    position: Tuple[float, float, float] = field(init=False)


@dataclass
class pmdpyTypeLoadIK():
    bone_id: int = field(init=False)
    bone_to: int = field(init=False)
    length: int = field(init=False)
    iteration: int = field(init=False)
    weight: float = field(init=False)
    child_bone_id: List[int] = field(init=False)


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
class pmdpyType():
    filename: str = field(default="")
    path: str = field(default="")
    ext: str = field(default="")
    directory: str = field(default="")

    version: str = field(default="")
    name: str = field(default="")
    comment: str = field(default="")

    # load file struct
    vertex: List[pmdpyTypeLoadVertex] = field(init=False)
    face: List[Tuple[int, int, int]] = field(init=False)
    material: List[pmdpyTypeLoadMaterial] = field(init=False)
    bone: List[pmdpyTypeLoadBone] = field(init=False)
    ik: List[pmdpyTypeLoadIK] = field(init=False)
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
