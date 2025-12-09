import numpy as np
from . import mmdpy_texture
from dataclasses import dataclass, field
from typing import Any


# model info
@dataclass
class mmdpyTypeVertex():
    ver: np.ndarray = field(init=False)
    nor: np.ndarray = field(init=False)
    uv: np.ndarray = field(init=False)
    bone_id: np.ndarray = field(init=False)
    bone_weight: np.ndarray = field(init=False)
    edge: int = field(init=False)


@dataclass
class mmdpyTypeMaterial():
    diffuse: np.ndarray = field(init=False)
    alpha: float = field(init=False)
    specularity: np.ndarray = field(init=False)
    specular_color: np.ndarray = field(init=False)
    mirror_color: np.ndarray = field(init=False)
    toon_index: int = field(init=False)
    edge_size: float = field(init=False)
    face_vert_count: int = field(init=False)
    texture_name: str | bytes = field(init=False)

    top: int = field(default=0)
    size: int = field(default=0)
    texture_path: str = field(default="")
    texture: mmdpy_texture.mmdpyTexture | None = field(init=False)
    color: np.ndarray = field(init=False)
    both_side_flag: bool = False


@dataclass
class mmdpyTypeIK():
    bone_index: int = field(init=False)
    bone_effect_index: int = field(init=False)
    length: int = field(init=False)
    iteration: int = field(init=False)
    weight: np.ndarray = field(init=False)
    child_bones_index: list[int] = field(init=False)


@dataclass
class mmdpyTypeBone():
    id: int = field(init=False)
    name: str = field(init=False)
    bone_type: int = field(init=False)
    position: np.ndarray = field(init=False)
    bone: int = field(init=False)
    bone_next: int = field(init=False)
    weight: float = field(init=False)
    parent_id: int = field(init=False)
    tail_id: int = field(init=False)
    ik_parent_id: int = field(init=False)
    ik: None | mmdpyTypeIK = field(default=None)
    rotatable_control: Any = field(init=False)

    level: int = field(default=0)  # 実行順の階層
    grant_rotation_parent_bone_index: Any = field(default=None)
    grant_rotation_parent_rate: float = field(default=0)
    grant_translate_parent_bone_index: Any = field(default=None)
    grant_translate_parent_rate: float = field(default=0)


@dataclass
class mmdpyTypePhysicsBody():
    index: int = field(init=False)
    bid: Any = field(init=False)
    cid: Any = field(init=False)

    name: str = field(init=False)
    bone_id: int = field(init=False)
    group_id: int = field(init=False)
    group_mask: str = field(init=False)
    type_id: int = field(init=False)
    sizes: np.ndarray = field(init=False)
    pos: np.ndarray = field(init=False)
    rot: np.ndarray = field(init=False)
    mass: float = field(init=False)
    pos_dim: float = field(init=False)
    rot_dim: float = field(init=False)
    recoil: float = field(init=False)
    friction: float = field(init=False)
    calc: int = field(init=False)
    bone: Any = field(init=False)


@dataclass
class mmdpyTypePhysicsJoint():
    cid: Any = field(init=False)

    name: str = field(init=False)
    rigidbody_a: int = field(init=False)
    rigidbody_b: int = field(init=False)
    pos: np.ndarray = field(init=False)
    rot: np.ndarray = field(init=False)
    constrain_pos: list[np.ndarray] = field(init=False)
    spring_pos: np.ndarray = field(init=False)
    spring_rot: np.ndarray = field(init=False)


@dataclass
class mmdpyTypePhysics():
    body: list[mmdpyTypePhysicsBody] = field(init=False)
    joint: list[mmdpyTypePhysicsJoint] = field(init=False)


# @dataclass 
class glslInfoClass():
    glsl_vao: Any = field(init=False)
    face_size: int = field(init=False)
    texture: mmdpy_texture.mmdpyTexture = field(init=False)
    color: np.ndarray = field(default=np.zeros([4]))
    alpha: float = field(init=False)
    matrices: np.ndarray = field(default=np.identity(4))

    indexes: np.ndarray = field(init=False)
    weights: np.ndarray = field(init=False)
    material: mmdpyTypeMaterial = field(init=False)


class mmdpyTypeModel:
    def __init__(self):
        # Adjusted struct
        self.vertices: list[mmdpyTypeVertex] = []
        self.faces: list[list[int]] = []
        self.materials: list[mmdpyTypeMaterial] = []
        self.bones: list[mmdpyTypeBone] = []
        self.physics_flag: bool = False
        self.physics: None | mmdpyTypePhysics = None
