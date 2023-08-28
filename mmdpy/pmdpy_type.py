from typing import Any
from dataclasses import dataclass, field


@dataclass
class pmdpyTypeLoadVertex():
    ver: tuple[float, float, float] = field(init=False)
    nor: tuple[float, float, float] = field(init=False)
    uv: tuple[float, float] = field(init=False)
    bone_id: tuple[int, int] = field(init=False)
    bone_weight: tuple[float, float] = field(init=False)
    edge: int = field(init=False)


@dataclass
class pmdpyTypeLoadMaterial():
    diffuse: tuple[float, float, float] = field(init=False)
    alpha: float = field(init=False)
    specularity: tuple[float, float, float] = field(init=False)
    specular_color: tuple[float, float, float] = field(init=False)
    mirror_color: tuple[float, float, float] = field(init=False)
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
    position: tuple[float, float, float] = field(init=False)


@dataclass
class pmdpyTypeLoadIK():
    bone_id: int = field(init=False)
    bone_to: int = field(init=False)
    length: int = field(init=False)
    iteration: int = field(init=False)
    weight: float = field(init=False)
    child_bone_id: list[int] = field(init=False)


@dataclass
class pmdpyTypeLoadSkin():
    name: str = field(init=False)
    var_size: int = field(init=False)
    type: int = field(init=False)
    var_id: list[int] = field(init=False)
    ver_offset: list[tuple[float, float, float]] = field(init=False)


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
    pos: tuple[Any, ...] = field(init=False)
    rot: tuple[Any, ...] = field(init=False)
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
    pos: tuple[Any, ...] = field(init=False)
    rot: tuple[Any, ...] = field(init=False)
    constrain_pos: list[tuple[Any, ...]] = field(init=False)
    spring_pos: tuple[Any, ...] = field(init=False)
    spring_rot: tuple[Any, ...] = field(init=False)


@dataclass
class pmdpyLoadPhysics():
    body: list[pmdpyTypeLoadPhysicsBody] = field(init=False)
    joint: list[pmdpyTypeLoadPhysicsJoint] = field(init=False)


@dataclass
class pmdpyTypeAdjustVertex():
    ver: tuple[Any, ...] = field(init=False)
    nor: tuple[Any, ...] = field(init=False)
    uv: tuple[Any, ...] = field(init=False)
    bone_id: tuple[Any, ...] = field(init=False)
    bone_weight: tuple[Any, ...] = field(init=False)
    edge: int = field(init=False)


@dataclass
class pmdpyTypeBone():
    bone_me: Any | int = field(init=False)
    bone_to: Any | int = field(init=False)
    len: int = field(init=False)
    iteration: int = field(init=False)
    weight: Any = field(init=False)
    child_bones: Any = field(init=False)
    ik: Any = field(init=False)


@dataclass
class pmdpyTypeAdjustIK():
    bone_me: Any | int = field(init=False)
    bone_to: Any | int = field(init=False)
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
    vertex: list[pmdpyTypeLoadVertex] = field(init=False)
    face: list[tuple[int, int, int]] = field(init=False)
    material: list[pmdpyTypeLoadMaterial] = field(init=False)
    bone: list[pmdpyTypeLoadBone] = field(init=False)
    ik: list[pmdpyTypeLoadIK] = field(init=False)
    skin: list[pmdpyTypeLoadSkin] = field(init=False)
    skin_name: list[int] = field(init=False)
    bone_frame_name: list[str] = field(init=False)
    bone_number: list[pmdpyTypeLoadBoneName] = field(init=False)

    english_flag: bool = field(init=False)
    english_head: dict[str, str] = field(init=False)
    bone_name_eng: list[str] = field(init=False)
    skin_name_eng: list[str] = field(init=False)
    bone_disp_name_eng: list[str] = field(init=False)

    toon_name: list[str] = field(init=False)
    physics_flag: bool = field(init=False)
    physics: None | pmdpyLoadPhysics = field(init=False)
