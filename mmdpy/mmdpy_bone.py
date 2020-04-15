import numpy as np


def normalize(v):
    nor = np.linalg.norm(v)
    return v / (nor + 1e-32)

class mmdpyBone:
    def __init__(self, index, bone_type, name, position, weight, ik_rotatable_control):
        self.id = index
        self.type = bone_type
        self.name = name
        self.weight = weight

        self.top_position = np.array(position)
        self.end_position = np.array(position)  # 初期は方向無し

        self.top_matrix = np.identity(4)
        self.top_matrix[3, 0] = position[0]
        self.top_matrix[3, 1] = position[1]
        self.top_matrix[3, 2] = position[2]

        # ik で必要
        self.offset_matrix = np.linalg.inv(self.top_matrix)
        # self.matrix = self.top_matrix * self.offset_matrix  # こんな関係

        # 変化量マトリックス
        self.delta_matrix = np.identity(4)
        self.local_matrix = np.identity(4)  # 表示時のローカルマトリックス

        # パートマトリックス
        self.part_matrix = np.identity(4)
        # self.matrix = self.part_matrix * (self.parent.part_matrix ...) * self.offset_matrix  # こんな関係
        # self.part_matrix * (self.parent.part_matrix ...) = self.top_matrix な関係

        # Offset をかけることで global matrix になる行列
        self.global_matrix = self.top_matrix

        self.parent = None
        self.child_bones = []

        self.ik_rotatable_control = ik_rotatable_control

    # 親ボーン設定
    def setParentBone(self, parent):
        if self.id < parent.id:
            return
        self.parent = parent
        parent.child_bones.append(self)
        self.part_matrix = np.matmul(self.top_matrix, self.parent.offset_matrix)

    # ボーンのグローバル座標から見た始点を返す
    def getLocalMatrix(self):
        return self.offset_matrix

    # 今のボーンを更新
    def updateMatrix(self, count_flag=False):
        if count_flag:
            if self.update_matrix_count > 0:
                return self.global_matrix
            self.update_matrix_count += 1

        local_matrix = np.identity(4)
        global_matrix = self.top_matrix
        if self.parent is not None:
            parent_matrix = self.parent.updateMatrix()
            global_matrix = np.matmul(self.part_matrix, parent_matrix)  # ボーンのローカル座標系に変換
        global_matrix = np.matmul(self.delta_matrix, global_matrix)  # 移動量を反映

        local_matrix = np.matmul(local_matrix, self.offset_matrix)  # ボーンのローカル座標系に変換
        local_matrix = np.matmul(local_matrix, global_matrix)  # グローバル座標系に変換
        self.local_matrix = local_matrix
        self.global_matrix = global_matrix
        return self.global_matrix

    # ボーンの更新処理準備
    def initUpdateMatrix(self):
        self.update_matrix_count = 0

    # ボーン構造表示
    def printChilds(self, indent=0):
        if indent > 32:
            print("/**** **** **** **** [ERROR] **** **** **** ****/")
            print(self.name)
            print("/**** **** **** **** [ERROR] **** **** **** ****/")
            raise RecursionError

        print("  " * indent + "{0}:".format(self.id) + "{0}".format(self.name))
        for c in self.child_bones:
            c.printChilds(indent=indent + 1)

    def addMatrix(self, matrix, overwrite=False):
        if overwrite:
            self.delta_matrix = matrix
        self.delta_matrix = np.matmul(matrix, self.delta_matrix)
        return self

    # position
    def getPosition(self):
        return self.global_matrix[3, 0: 3]

    # スライドさせる
    def slide(self, p):
        matrix = np.identity(4)
        matrix[3, 0] = p[0]
        matrix[3, 1] = p[1]
        matrix[3, 2] = p[2]
        return self.addMatrix(matrix)

    # ik 付き
    def move(self, target, chain=None, loop_size=1, depth=1):
        if chain is None:
            chain = []
            parent = self
            for _ in range(depth):
                parent = parent.parent
                if parent is None:
                    break
                chain.append(parent)
        effect_bone = self

        target_matrix = np.identity(4)
        target_matrix[3, :3] = list(target)
        for _ in range(loop_size):  # ik step
            for c in chain:
                effector_matrix = c.updateMatrix()
                inv_coord = np.linalg.inv(effector_matrix)

                # 目的地
                local_target_pos = np.matmul(target_matrix, inv_coord)[3, :3]
                local_target_pos = normalize(local_target_pos)

                # 向かうボーンの方向
                local_effect_pos = np.matmul(effect_bone.updateMatrix(), inv_coord)[3, :3]
                local_effect_pos = normalize(local_effect_pos)

                # 離れ具合を測る
                d = np.inner(local_effect_pos, local_target_pos)
                d = +1 if d > +1 else d
                d = -1 if d < -1 else d

                # 移動予定角度を指定
                rot = np.arccos(d)

                # 回転軸を計算
                axis = np.cross(local_effect_pos, local_target_pos)

                # 回転制御付き回転
                c.ik_rotatable_control(c, axis, rot)

        return self

    def rot(self, axis, r, overwrite=False, update_flag=True):
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
        return self.addMatrix(matrix, overwrite=overwrite)

    def rotX(self, rot, overwrite=False, update_flag=True):
        matrix = np.identity(4)
        matrix[1, 1] = np.cos(rot)
        matrix[1, 2] = np.sin(rot)
        matrix[2, 1] = -np.sin(rot)
        matrix[2, 2] = np.cos(rot)
        if not update_flag:
            return matrix
        return self.addMatrix(matrix, overwrite=overwrite)

    def rotY(self, rot, overwrite=False, update_flag=True):
        matrix = np.identity(4)
        matrix[0, 0] = np.cos(rot)
        matrix[0, 2] = -np.sin(rot)
        matrix[2, 0] = np.sin(rot)
        matrix[2, 2] = np.cos(rot)
        if not update_flag:
            return matrix
        return self.addMatrix(matrix, overwrite=overwrite)

    def rotZ(self, rot, overwrite=False, update_flag=True):
        matrix = np.identity(4)
        matrix[0, 0] = np.cos(rot)
        matrix[0, 1] = np.sin(rot)
        matrix[1, 0] = -np.sin(rot)
        matrix[1, 1] = np.cos(rot)
        if not update_flag:
            return matrix
        return self.addMatrix(matrix, overwrite=overwrite)
