import numpy as np
from typing import Any
import scipy.spatial.transform.rotation as scipyrot
import math


def normalize(v: np.ndarray) -> np.ndarray:
    nor = np.linalg.norm(v)
    return v / (nor + 1e-32)


def rotation_matrix_3d(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if np.array_equal(a, b):
        return np.identity(3)
    if np.array_equal(a, -b):
        return -np.identity(3)
    s = a + b
    return 2.0 * np.outer(s, s) / np.dot(s, s) - np.identity(3)


class mmdpyIK:
    def __init__(self, bone: Any, next_bone: Any, iteration: int, child_bones: list[Any]):
        self.bone: Any = bone
        self.effect_bone: Any = next_bone
        self.iteration: int = iteration
        self.child_bones: list[Any] = child_bones


class mmdpyBone:
    def __init__(self,
                 index: int, name: str, level: int,
                 position: np.ndarray, weight: float,
                 rotatable_control: Any):
        self.id: int = index
        self.level: int = level
        self.name: str = name
        self.weight: float = weight

        self.top_position: np.ndarray = np.array(position)
        self.end_position: np.ndarray = np.array(position)  # 初期は方向無し

        self.top_matrix: np.ndarray = np.identity(4)
        self.top_matrix[3, 0] = position[0]
        self.top_matrix[3, 1] = position[1]
        self.top_matrix[3, 2] = position[2]

        # ik で必要
        self.offset_matrix: np.ndarray = np.linalg.inv(self.top_matrix)
        # self.matrix: np.ndarray = self.top_matrix * self.offset_matrix  # こんな関係

        # 変化量マトリックス
        self.delta_matrix: np.ndarray = np.identity(4)
        self.local_matrix: np.ndarray = np.identity(4)  # 表示時のローカルマトリックス

        # パートマトリックス
        self.part_matrix: np.ndarray = np.identity(4)
        # self.matrix = self.part_matrix * (self.parent.part_matrix ...) * self.offset_matrix  # こんな関係
        # self.part_matrix * (self.parent.part_matrix ...) = self.top_matrix な関係

        # Offset をかけることで global matrix になる行列
        self.global_matrix: np.ndarray = self.top_matrix

        self.parent: None | mmdpyBone = None
        self.child_bones: list[mmdpyBone] = []

        self.rotatable_control = rotatable_control

        self.rotate: np.ndarray = np.zeros(3)

        # 読み込みデータ保存
        self.data: Any = None
        self.ik: None | mmdpyIK = None

        self.grant_rotation_parent_bone: Any = None
        self.grant_rotation_parent_rate: float = 0
        self.grant_translate_parent_bone: Any = None
        self.grant_translate_parent_rate: float = 0

        self.updated_flag: bool = False

    # 実行順序
    # pmd ではすべて 0
    # pmx にはIKや付与など実行順序がある
    def get_level(self) -> int:
        return self.level

    # 追従して動くボーンを設定
    # 回転付与
    def set_grant_rotation_parent_bone(self, bone: Any, rate: float) -> None:
        self.grant_rotation_parent_bone = bone
        self.grant_rotation_parent_rate = rate

    # 移動付与
    def set_grant_translate_parent_bone(self, bone: Any, rate: float) -> None:
        self.grant_translate_parent_bone = bone
        self.grant_translate_parent_rate = rate

    # ik
    def set_ik(self, ik: mmdpyIK):
        self.ik = ik

    def get_ik(self) -> None | mmdpyIK:
        return self.ik

    # 方向計算
    def calc_rotate(self, next_bone) -> np.ndarray:
        rotmat: np.ndarray = rotation_matrix_3d(next_bone.get_position(), self.get_position())
        self.rotate = scipyrot.Rotation.from_matrix(rotmat).as_euler(seq="xyz")
        return self.rotate

    # 子ボーンからボーンの方向を計算
    def calc_rotate_from_child(self) -> np.ndarray:
        self.rotate = np.zeros(3)
        if len(self.child_bones) == 0:
            return self.rotate
        for c in self.child_bones:
            self.rotate += self.calc_rotate(c)
        return self.rotate / len(self.child_bones)

    # 親ボーン設定
    def set_parent_bone(self, parent):
        if self.id < parent.id:
            return
        self.parent = parent
        parent.child_bones.append(self)
        if self.parent is not None:
            self.part_matrix = np.matmul(self.top_matrix, self.parent.offset_matrix)

    # ボーンのグローバル座標から見た始点を返す
    def get_local_matrix(self):
        return self.offset_matrix

    # 更新処理をフラグで管理し処理を軽量化
    def reset_updated_flag(self) -> None:
        self.updated_flag = False

    # グローバルマトリックスを返す
    def get_global_matrix_with_flag(self) -> np.ndarray:
        if self.updated_flag:
            return self.global_matrix
        global_matrix: np.ndarray = self.top_matrix
        if self.parent is not None:
            parent_matrix: np.ndarray = self.parent.get_global_matrix_with_flag()
            global_matrix = np.matmul(self.part_matrix, parent_matrix)  # ボーンのローカル座標系に変換
        return np.matmul(self.delta_matrix, global_matrix)  # 移動量を反映

    def get_global_matrix(self) -> np.ndarray:
        global_matrix: np.ndarray = self.top_matrix
        if self.parent is not None:
            parent_matrix: np.ndarray = self.parent.get_global_matrix()
            global_matrix = np.matmul(self.part_matrix, parent_matrix)  # ボーンのローカル座標系に変換
        return np.matmul(self.delta_matrix, global_matrix)  # 移動量を反映

    # 今のボーンを更新
    def update_matrix(self) -> np.ndarray:
        if self.parent and not self.parent.updated_flag:
            self.parent.update_matrix()
        self.global_matrix = self.get_global_matrix_with_flag()
        self.local_matrix = np.matmul(self.offset_matrix, self.global_matrix)  # ボーンのローカル座標系に変換、グローバル座標系に変換
        # if self.parent is not None:
        #     self.parent.calc_rotate(self)
        self.updated_flag = True
        return self.global_matrix

    # ボーン構造表示
    def print_childs(self, indent: str = "", last_flag: bool = False):
        if len(indent) > 32:
            print("/**** **** **** **** [ERROR] **** **** **** ****/")
            print(self.name)
            print("/**** **** **** **** [ERROR] **** **** **** ****/")
            raise RecursionError

        my_indent = "┃ "
        tree_string = "┣ "
        if last_flag:
            my_indent = "  "
            tree_string = "┗ "
        if indent == "":
            my_indent = "  "
            tree_string = "  "
        print(indent + tree_string + "{0}:".format(self.id) + "{0}".format(self.name))
        for i, c in enumerate(self.child_bones):
            c.print_childs(indent=indent + my_indent, last_flag=(i == len(self.child_bones) - 1))

    def add_matrix(self, matrix: np.ndarray, overwrite=False):
        if overwrite:
            self.delta_matrix = matrix
        self.delta_matrix = np.matmul(matrix, self.delta_matrix)
        return self

    # position
    def get_position(self) -> np.ndarray:
        return self.global_matrix[3, 0: 3]

    def set_position(self, p: list[float] | np.ndarray) -> list[float] | np.ndarray:
        self.global_matrix[3, 0: 3] = p
        return p

    # euler
    def get_euler(self, option: str) -> np.ndarray:
        rot = scipyrot.Rotation.from_matrix(self.global_matrix[0:3, 0:3])
        q = rot.as_euler(option)
        return q

    def set_euler(self, e: list[float] | np.ndarray, option: str) -> np.ndarray:
        rot = scipyrot.Rotation.from_euler(option, e)
        m = rot.as_matrix()
        self.global_matrix[0:3, 0:3] = m
        return self.global_matrix

    # quaternion
    def get_quaternion(self) -> np.ndarray:
        rot = scipyrot.Rotation.from_matrix(self.global_matrix[0:3, 0:3])
        q = rot.as_quat()
        return q

    def get_quaternion_scipy(self) -> np.ndarray:
        rot = scipyrot.Rotation.from_matrix(self.global_matrix[0:3, 0:3])
        return rot

    def set_quaternion(self, q: list[float] | np.ndarray) -> np.ndarray:
        rot = scipyrot.Rotation.from_quat(q)
        m = rot.as_matrix()
        self.global_matrix[0:3, 0:3] = m
        return self.global_matrix

    # rotation matrix
    def get_rotmatrix(self) -> np.ndarray:
        return self.global_matrix[0:3, 0:3]

    def set_rotmatrix(self, m: np.ndarray) -> np.ndarray:
        self.global_matrix[0:3, 0:3] = m
        return m

    # matrix
    def get_matrix(self) -> np.ndarray:
        return self.global_matrix

    def set_matrix(self, m: np.ndarray) -> np.ndarray:
        self.global_matrix = m
        return m

    # 変化量
    # position
    def get_position_delta(self) -> np.ndarray:
        return self.delta_matrix[3, 0: 3]

    # quaternion
    def get_quaternion_delta(self) -> np.ndarray:
        rot = scipyrot.Rotation.from_matrix(self.delta_matrix[0:3, 0:3])
        q = rot.as_quat()
        return q

    # matrix
    def get_rotmatrix_delta(self) -> np.ndarray:
        return self.delta_matrix[0:3, 0:3]

    # スライドさせる
    def slide(self, p: list[float] | np.ndarray):
        matrix = np.identity(4)
        matrix[3, 0] = p[0]
        matrix[3, 1] = p[1]
        matrix[3, 2] = p[2]
        return self.add_matrix(matrix)

    # ik 付き
    def move(self, target_position: list[float] | np.ndarray,
             chain: None | list[Any] = None,
             loop_size: int = 1, depth: int = 0, loop_range: int = 255):
        bias = 1e-2
        if loop_size > loop_range:
            loop_size = loop_range

        effect_bone: mmdpyBone = self
        if chain is None:
            chain = []
            parent: mmdpyBone = self
            for _ in range(depth):
                if parent.parent is not None:
                    parent = parent.parent
                    chain.append(parent)

        target_matrix = np.identity(4)
        target_matrix[3, :3] = np.array(target_position)
        for c in chain:
            rot = 0
            conflag = True
            for _ in range(loop_size):  # ik step
                effector_matrix = c.get_global_matrix()
                base_matrix = np.linalg.inv(effector_matrix)

                # 目的地
                local_target_pos = np.matmul(target_matrix, base_matrix)[3, :3]
                local_target_pos = normalize(local_target_pos)

                # 向かうボーンの方向
                local_effect_pos = np.matmul(effect_bone.get_global_matrix(), base_matrix)[3, :3]
                local_effect_pos = normalize(local_effect_pos)

                # 離れ具合を測る
                dot_value = np.clip(np.inner(local_effect_pos, local_target_pos), -1, +1)

                # 移動予定角度を指定
                rot = np.arccos(dot_value)
                if abs(rot) < bias:
                    conflag = False
                    break

                # 回転軸を計算
                axis = np.cross(local_effect_pos, local_target_pos)
                if np.sum(np.abs(axis)) < bias:
                    conflag = False
                    break
                axis = normalize(axis)

                # 回転制御付き回転
                c.rotatable_control(c, axis, rot)

            if not conflag:
                break

        return self

    def rot(self, axis: np.ndarray, r: float, overwrite: bool = False, update_flag: bool = True):
        axis = normalize(axis)
        matrix = np.identity(4)

        sin_r = math.sin(r)
        cos_r = math.cos(r)
        c = 1.00 - cos_r

        x, y, z = list(axis)
        matrix[0, 0] = x * x * c + cos_r
        matrix[0, 1] = x * y * c + z * sin_r
        matrix[0, 2] = x * z * c - y * sin_r

        matrix[1, 0] = y * x * c - z * sin_r
        matrix[1, 1] = y * y * c + cos_r
        matrix[1, 2] = y * z * c + x * sin_r

        matrix[2, 0] = z * x * c + y * sin_r
        matrix[2, 1] = z * y * c - x * sin_r
        matrix[2, 2] = z * z * c + cos_r
        if not update_flag:
            return matrix
        return self.add_matrix(matrix, overwrite=overwrite)

    def set_rot(self, x, y, z, overwrite: bool = False, update_flag: bool = True):
        sinx = np.sin(x)
        cosx = np.cos(x)

        siny = np.sin(y)
        cosy = np.cos(y)

        sinz = np.sin(z)
        cosz = np.cos(z)

        matrix = np.identity(4)

        matrix[0][0] = cosy * cosz - sinx * siny * sinz
        matrix[0][1] = -cosx * sinz
        matrix[0][2] = siny * cosz + sinx * cosy * sinz

        matrix[1][0] = cosy * sinz + sinx * siny * cosz
        matrix[1][1] = cosx * cosz
        matrix[1][2] = sinz * siny - sinx * cosy * cosz

        matrix[2][0] = -cosx * siny
        matrix[2][1] = sinx
        matrix[2][2] = cosx * cosy

        if not update_flag:
            return matrix
        return self.add_matrix(matrix, overwrite=overwrite)

    def rotX(self, rot: float, overwrite=False, update_flag=True):
        matrix = np.identity(4)
        matrix[1, 1] = np.cos(rot)
        matrix[1, 2] = np.sin(rot)
        matrix[2, 1] = -np.sin(rot)
        matrix[2, 2] = np.cos(rot)
        if not update_flag:
            return matrix
        return self.add_matrix(matrix, overwrite=overwrite)

    def rotY(self, rot: float, overwrite=False, update_flag=True):
        matrix = np.identity(4)
        matrix[0, 0] = np.cos(rot)
        matrix[0, 2] = -np.sin(rot)
        matrix[2, 0] = np.sin(rot)
        matrix[2, 2] = np.cos(rot)
        if not update_flag:
            return matrix
        return self.add_matrix(matrix, overwrite=overwrite)

    def rotZ(self, rot: float, overwrite=False, update_flag=True):
        matrix = np.identity(4)
        matrix[0, 0] = np.cos(rot)
        matrix[0, 1] = np.sin(rot)
        matrix[1, 0] = -np.sin(rot)
        matrix[1, 1] = np.cos(rot)
        if not update_flag:
            return matrix
        return self.add_matrix(matrix, overwrite=overwrite)

    def get_rot(self, matrix_type=lambda x: x.global_matrix):
        threshold: float = 0.001
        m = matrix_type(self)

        angle_x: float = 0.00
        angle_y: float = 0.00
        angle_z: float = 0.00
        if abs(m[2][1] - 1) < threshold:
            angle_x = np.pi / 2.00
            angle_y = 0
            angle_x = np.arctan2(m[1][0], m[0][0])
        elif abs(m[2][1] + 1) < threshold:
            angle_x = -np.pi / 2.00
            angle_y = 0
            angle_x = np.arctan2(m[1][0], m[0][0])
        else:
            angle_x = np.arcsin(m[2][1])
            angle_y = np.arctan2(-m[2][0], m[2][2])
            angle_z = np.arctan2(-m[0][1], m[1][1])

        return (angle_x, angle_y, angle_z)

    # 追従動作
    def grant(self) -> None:
        # 回転
        if self.grant_rotation_parent_bone is not None:
            r = self.grant_rotation_parent_rate
            x, y, z = self.grant_rotation_parent_bone.get_rot(lambda x: x.delta_matrix)
            self.set_rot(x * r, y * r, z * r, update_flag=True)

        # 移動
        if self.grant_translate_parent_bone is not None:
            r = self.grant_translate_parent_rate
            p = self.grant_translate_parent_bone.get_position() * r
            self.set_position(p)
