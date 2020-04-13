import copy

import mmdpy_root
import mmdpy_mesh
import mmdpy_shader
import mmdpy_bone

MMDPY_MATERIAL_USING_BONE_NUM = mmdpy_root.MMDPY_MATERIAL_USING_BONE_NUM


class mmdpyModel:
    def __init__(self):
        self.meshes = []

        self.polygon_vertex_size = 3
        self.vertex_range = 0xffff - 0xffff % self.polygon_vertex_size
        # self.vertex_range = 256 - 256 % self.polygon_vertex_size

        self.shader = mmdpy_shader.mmdpyShader()

    def draw(self):
        for m in self.meshes:
            m.draw()

    def createBones(self, data):
        self.bones = []
        self.name2bone = {}

        for bi in data.bones:
            b = mmdpy_bone.mmdpyBone(bi.id, bi.bone_type, bi.name, bi.position, bi.weight, bi.ik_rotatable_control)
            self.bones.append(b)
        for b, bi in zip(self.bones, data.bones):
            b.setParentBone(self.bones[bi.parent_id])
            self.name2bone[b.name] = b.id
            b.data = bi
            b.ik = bi.ik

        # ik
        for b in data.bones:
            if b.ik is not None:
                b.ik.child_bones = [self.getBoneByName(b.name) for b in b.ik.child_bones]
                b.ik.bone_me = self.getBoneByName(b.ik.bone_me.name)
                b.ik.bone_to = self.getBoneByName(b.ik.bone_to.name)

    def getBone(self, index=0):
        return self.bones[index]

    def getBoneByName(self, name):
        if not name in self.name2bone.keys():
            return None
        index = self.name2bone[name]
        return self.getBone(index)

    # モデルを mmdpy_root.Config の設定どおりにリメイク
    def setModel(self, data):
        self.createBones(data)

        material_id = 0

        # Vertex adjust
        is_vertex_range = False     # 頂点が上限値
        is_update_material = False  # マテリアルの更新
        is_bone_range = False       # ボーンインデックスが上限値

        new_vertex = []
        new_face = []
        using_bones = [0] * len(data.bones)
        using_bones[0] = 1
        new_bone_id = [0] + [None] * (MMDPY_MATERIAL_USING_BONE_NUM - 1)
        rawbone_2_newbone = [0] * len(data.bones)
        bone_counter = 1
        oldv_2_newv = [None] * len(data.face)
        for fi, fs in enumerate(data.faces):
            # 表現しきれない頂点インデックスのひらき
            if max(fs) - min(fs) >= self.vertex_range - self.polygon_vertex_size:
                is_vertex_range = True
                # Error

            # マテリアル内のインデックスを頂点インデックスが超えた
            # メッシュを生成する
            if data.materials[material_id].size + data.materials[material_id].top <= self.polygon_vertex_size * fi:
                is_update_material = True

            # Mesh 追加
            if is_vertex_range or is_update_material or is_bone_range:
                mesh = mmdpy_mesh.mmdpyMesh(len(self.meshes), self.shader, new_vertex, new_face, data.materials[material_id], [self.bones[i] for i in new_bone_id if i is not None])
                self.meshes.append(mesh)

                # 対応するマテリアルインデックスも更新
                if is_update_material:
                    material_id += 1

                is_vertex_range = False
                is_update_material = False
                is_bone_range = False

                new_vertex = []
                new_face = []
                using_bones = [0] * len(data.bones)
                using_bones[0] = 1
                new_bone_id = [0] + [None] * (MMDPY_MATERIAL_USING_BONE_NUM - 1)
                rawbone_2_newbone = [0] * len(data.bones)
                bone_counter = 1
                oldv_2_newv = [None] * len(data.face)

            # 一つ一つの頂点インデックスを設定
            # 読み込んだ頂点を新頂点へ転写
            for vi in fs:
                new_vi = len(new_vertex)
                if oldv_2_newv[vi] is None:  # 新頂点が未設定
                    v = copy.deepcopy(data.vertices[vi])
                    oldv_2_newv[vi] = len(new_vertex)

                    v.bone_id = [0, 0, 0, 0]
                    for i, vbone_i in enumerate(data.vertices[vi].bone_id):
                        if using_bones[vbone_i] == 0:
                            new_bone_id[bone_counter] = vbone_i
                            rawbone_2_newbone[vbone_i] = bone_counter
                            bone_counter += 1
                            if bone_counter >= MMDPY_MATERIAL_USING_BONE_NUM - 1:
                                is_bone_range = True

                        v.bone_id[i] = rawbone_2_newbone[vbone_i]
                        using_bones[vbone_i] += 1

                    new_vertex.append(v)
                    if len(new_vertex) >= self.vertex_range - self.polygon_vertex_size:
                        is_vertex_range = True
                else:
                    # 新頂点設定済み
                    new_vi = oldv_2_newv[vi]

                # 頂点インデックス追加
                new_face.append(new_vi)

        mesh = mmdpy_mesh.mmdpyMesh(len(self.meshes), self.shader, new_vertex, new_face, data.materials[material_id], [self.bones[i] for i in new_bone_id if i is not None])
        self.meshes.append(mesh)

        return True
