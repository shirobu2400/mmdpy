import numpy as np
import quaternion
from typing import Any, List, Union


def normalize(v):
    nor = np.linalg.norm(v)
    return v / (nor + 1e-32)


class mmdpyIK:
    def __init__(self, bone: Any, next_bone: Any, length: int, iteration: int, weight: np.ndarray, child_bones: List):
        self.bone: Any = bone
        self.effect_bone: Any = next_bone
        self.length: int = length
        self.iteration: int = iteration
        self.weight: np.ndarray = weight
        self.child_bones: List[Any] = child_bones


class mmdpyBone:
    def __init__(self, index: int, bone_type: int, name: str,
                 position: np.ndarray, weight: float, rotatable_control: Any):
        self.id: int = index
        self.type: int = bone_type
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

        self.parent: Union[None, mmdpyBone] = None
        self.child_bones: List[mmdpyBone] = []

        self.rotatable_control = rotatable_control

        # 読み込みデータ保存
        self.data: Any = None
        self.ik: Union[None, mmdpyIK] = None

        self.init_update_matrix()

    # ik
    def set_ik(self, ik: mmdpyIK):
        self.ik = ik

    def get_ik(self) -> Union[None, mmdpyIK]:
        return self.ik

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

    # 今のボーンを更新
    def update_matrix(self, count_flag: bool = False) -> np.ndarray:
        if count_flag:
            if self.update_matrix_count > 0:
                return self.global_matrix
            self.update_matrix_count += 1

        local_matrix = np.identity(4)
        global_matrix = self.top_matrix
        if self.parent is not None:
            parent_matrix = self.parent.update_matrix()
            global_matrix = np.matmul(self.part_matrix, parent_matrix)  # ボーンのローカル座標系に変換
        global_matrix = np.matmul(self.delta_matrix, global_matrix)  # 移動量を反映

        local_matrix = np.matmul(local_matrix, self.offset_matrix)  # ボーンのローカル座標系に変換
        local_matrix = np.matmul(local_matrix, global_matrix)  # グローバル座標系に変換
        self.local_matrix = local_matrix
        self.global_matrix = global_matrix
        return self.global_matrix

    # ボーンの更新処理準備
    def init_update_matrix(self):
        self.update_matrix_count = 0

    # 反映用のローカルマトリックスを強制的に変換
    def update_local_matrix(self) -> np.ndarray:
        local_matrix = np.identity(4)
        local_matrix = np.matmul(local_matrix, self.offset_matrix)  # ボーンのローカル座標系に変換
        local_matrix = np.matmul(local_matrix, self.global_matrix)  # グローバル座標系に変換
        self.local_matrix = local_matrix
        return self.local_matrix

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
    def get_position(self):
        return self.global_matrix[3, 0: 3]

    def set_position(self, p: Union[List[float], np.ndarray]) -> Union[List[float], np.ndarray]:
        self.global_matrix[3, 0: 3] = p
        return p

    # quaternion
    def get_quaternion(self):
        # q = quaternion.from_rotation_matrix(self.update_matrix()[0 :3, 0 :3])
        q = quaternion.from_rotation_matrix(self.global_matrix[:3, :3])
        q = quaternion.as_float_array(q)
        q = normalize(q)
        return q

    def set_quaternion(self, q: Union[List[float], np.ndarray]):
        q = quaternion.as_quat_array(q)
        q = quaternion.as_rotation_matrix(q)
        self.global_matrix[:3, :3] = q
        return self.global_matrix

    # スライドさせる
    def slide(self, p: Union[List[float], np.ndarray]):
        matrix = np.identity(4)
        matrix[3, 0] = p[0]
        matrix[3, 1] = p[1]
        matrix[3, 2] = p[2]
        return self.add_matrix(matrix)

    # ik 付き
    def move(self, target_position: Union[List[float], np.ndarray], chain: Union[None, List[Any]] = None,
             loop_size: int = 1, depth: int = 1, loop_range: int = 256):
        bias = 1e-4
        if loop_size > loop_range:
            loop_size = loop_range

        effect_bone = self
        if chain is None:
            chain = []
            parent: Any = self
            for _ in range(depth):
                parent = parent.parent
                if parent is not None:
                    chain.append(parent)

        target_matrix = np.identity(4)
        target_matrix[3, :3] = np.asarray(target_position)
        for _ in range(loop_size):  # ik step
            rot = 0
            for c in chain:
                effector_matrix = c.global_matrix
                base_matrix = np.linalg.inv(effector_matrix)

                # 目的地
                local_target_pos = np.matmul(target_matrix, base_matrix)[3, :3]
                dsum = np.sum(np.abs(local_target_pos))
                if np.isnan(dsum) or dsum < bias:
                    break
                local_target_pos = normalize(local_target_pos)

                # 向かうボーンの方向
                local_effect_pos = np.matmul(effect_bone.update_matrix(), base_matrix)[3, :3]
                dsum = np.sum(np.abs(local_effect_pos))
                if np.isnan(dsum) or dsum < bias:
                    break
                local_effect_pos = normalize(local_effect_pos)

                # 離れ具合を測る
                dot_value = np.clip(np.inner(local_effect_pos, local_target_pos), -1, +1)

                # 移動予定角度を指定
                rot = np.arccos(dot_value)
                if abs(rot) < bias:
                    break

                # 回転軸を計算
                axis = np.cross(local_effect_pos, local_target_pos)
                axis_sum = np.sum(np.abs(axis))
                if np.isnan(axis_sum) or axis_sum < bias:
                    break
                axis = normalize(axis)

                # 回転制御付き回転
                c.rotatable_control(c, axis, rot)

            if abs(rot) < bias:
                break

        return self

    def rot(self, axis: np.ndarray, r: float, overwrite: bool = False, update_flag: bool = True):
        if abs(r) < 1e-4:
            if not update_flag:
                return np.identity(4)
            return self

        axis = normalize(axis)
        matrix = np.identity(4)

        sin_r = np.sin(r)
        cos_r = np.cos(r)
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
