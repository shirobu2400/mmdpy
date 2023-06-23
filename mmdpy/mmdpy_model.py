from __future__ import annotations
import copy
import numpy as np
from typing import List, Union
import OpenGL.GL as gl
from . import mmdpy_root
from . import mmdpy_mesh
from . import mmdpy_shader
from . import mmdpy_type
from . import mmdpy_bone
from . import mmdpy_physics
# from . import mmdpy_physics_ode as mmdpy_physics


MMDPY_MATERIAL_USING_BONE_NUM = mmdpy_root.MMDPY_MATERIAL_USING_BONE_NUM


class mmdpyModel:
    def __init__(self):
        self.shader = mmdpy_shader.mmdpyShader()
        self.meshes: List[mmdpy_mesh.mmdpyMesh] = []

        # Polygon vertex size
        self.polygon_vertex_size: int = 3

        # Face size
        self.vertex_range: int = 0xffff - 0xffff % self.polygon_vertex_size
        # self.vertex_range = 256 - 256 % self.polygon_vertex_size

        self.name2bone = {}
        self.physics: Union[None, mmdpy_physics.mmdpyPhysics] = None

    def draw(self) -> None:
        self.draw_option_on()
        for m in self.meshes:
            m.draw()
        self.draw_option_off()

    def draw_option_on(self) -> None:
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def draw_option_off(self) -> None:
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_BLEND)

    def create_bones(self, data: mmdpy_type.mmdpyTypeModel) -> None:
        self.bones: List[mmdpy_bone.mmdpyBone] = [
            mmdpy_bone.mmdpyBone(
                bone.id, bone.name, bone.level,
                bone.position, bone.weight,
                bone.rotatable_control)
            for bone in data.bones]

        for i, bone_i in enumerate(data.bones):
            self.bones[i].set_parent_bone(self.bones[bone_i.parent_id])
            self.name2bone[bone_i.name] = bone_i.id
            self.bones[i].data = bone_i
            if bone_i.ik:
                ik_model = mmdpy_bone.mmdpyIK(
                    self.bones[i],
                    self.bones[bone_i.ik.bone_effect_index],
                    bone_i.ik.iteration,
                    [self.bones[i] for i in bone_i.ik.child_bones_index]
                )
                self.bones[i].set_ik(ik_model)
            if data.bones[i].grant_rotation_parent_bone_index is not None:
                self.bones[i].set_grant_rotation_parent_bone(
                    self.bones[data.bones[i].grant_rotation_parent_bone_index],
                    data.bones[i].grant_rotation_parent_rate
                )

            if data.bones[i].grant_translate_parent_bone_index is not None:
                self.bones[i].set_grant_translate_parent_bone(
                    self.bones[data.bones[i].grant_translate_parent_bone_index],
                    data.bones[i].grant_translate_parent_rate
                )

        self.ikbones: List[mmdpy_bone.mmdpyBone] = [x for x in self.bones if x.get_ik() is not None]

    def create_physics(self, physics_flag: bool, data: mmdpy_type.mmdpyTypeModel) -> None:
        # physics infomation
        if physics_flag and data.physics:
            self.physics = mmdpy_physics.mmdpyPhysics(self.bones, data.physics.body, data.physics.joint)

    def get_bone(self, index: int = 0) -> mmdpy_bone.mmdpyBone:
        return self.bones[index]

    def get_bone_by_name(self, name: str) -> mmdpy_bone.mmdpyBone:
        if name not in self.name2bone.keys():
            raise KeyError
        index = self.name2bone[name]
        return self.get_bone(index)

    # Bone Matrix update
    def update_bone(self) -> mmdpyModel:

        # レベルごとのボーン更新
        def update_bone_from_level(b: mmdpy_bone.mmdpyBone) -> None:
            # IK
            ikbone: Union[None, mmdpy_bone.mmdpyIK] = b.get_ik()
            if ikbone is not None:
                target_vector = b.get_global_matrix()[3, 0: 3]
                ikbone.effect_bone.move(target_vector, chain=ikbone.child_bones, loop_size=ikbone.iteration)

            # 付与
            b.grant()

        # 実行レベル順に実施
        level_max = max([x.get_level() for x in self.bones])
        for level in range(level_max + 1):
            blist: List[mmdpy_bone.mmdpyBone] = [x for x in self.bones if x.get_level() == level]
            for b in blist:
                update_bone_from_level(b)

        # ボーンの姿勢行列を更新
        for b in self.bones:
            b.reset_updated_flag()
        for b in self.bones:
            b.update_matrix()

        return self

    def update_physics(self) -> mmdpyModel:
        if self.physics is None:
            return self
        self.physics.run()
        return self

    # モデルを mmdpy_root.Config の設定どおりにリメイク
    def set_model(self, data: mmdpy_type.mmdpyTypeModel) -> bool:

        # Create bone and ik
        self.create_bones(data)

        material_id: int = 0
        face_length: int = len(data.faces)

        # Vertex adjust
        is_vertex_range: bool = False     # 頂点が上限値
        is_update_material: bool = False  # マテリアルの更新
        is_bone_range: bool = False       # ボーンインデックスが上限値

        new_vertex: List[mmdpy_type.mmdpyTypeVertex] = []
        new_face: List[int] = []
        using_bones: List[int] = [1] + [0] * (len(self.bones) - 1)
        new_bone_id: List[int] = [0] + [-1] * (MMDPY_MATERIAL_USING_BONE_NUM - 1)
        rawbone_2_newbone: List[int] = [0] * len(data.bones)
        bone_counter: int = 1
        oldv_2_newv: List[int] = [-1] * int(face_length)

        fi = 0
        while fi < face_length:
            fs = data.faces[fi]

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
                mesh = mmdpy_mesh.mmdpyMesh(len(self.meshes), self.shader, new_vertex, new_face,
                                            data.materials[material_id],
                                            [self.bones[i] for i in new_bone_id if not i < 0])
                self.meshes.append(mesh)

                # 対応するマテリアルインデックスも更新
                if is_update_material:
                    material_id += 1

                is_vertex_range = False
                is_update_material = False
                is_bone_range = False

                new_vertex = []
                new_face = []
                using_bones = [1] + [0] * (len(self.bones) - 1)
                new_bone_id = [0] + [-1] * (MMDPY_MATERIAL_USING_BONE_NUM - 1)
                rawbone_2_newbone = [0] * len(data.bones)
                bone_counter = 1
                oldv_2_newv = [-1] * int(len(data.faces))

            # 一つ一つの頂点インデックスを設定
            # 読み込んだ頂点を新頂点へ転写
            for vi in fs:
                new_vi = len(new_vertex)
                if oldv_2_newv[vi] < 0:  # 新頂点が未設定
                    v = copy.deepcopy(data.vertices[vi])
                    oldv_2_newv[vi] = len(new_vertex)

                    v.bone_id = np.zeros([4])
                    for i, vbone_i in enumerate(data.vertices[vi].bone_id):
                        if using_bones[vbone_i] == 0:
                            new_bone_id[bone_counter] = vbone_i
                            rawbone_2_newbone[vbone_i] = bone_counter
                            bone_counter += 1
                        if MMDPY_MATERIAL_USING_BONE_NUM - 3 <= bone_counter or len(new_bone_id) <= bone_counter:
                            is_bone_range = True
                            break

                        v.bone_id[i] = rawbone_2_newbone[vbone_i]
                        using_bones[vbone_i] += 1

                    if is_bone_range:
                        break
                    if len(new_vertex) >= self.vertex_range - self.polygon_vertex_size:
                        is_vertex_range = True
                        break
                    new_vertex.append(v)
                else:
                    # 新頂点設定済み
                    new_vi = oldv_2_newv[vi]

                if is_bone_range or is_vertex_range:
                    # 対象の面をやり直し
                    fi -= 1
                    break

                # 頂点インデックス追加
                new_face.append(new_vi)

            # 面をインクリメント
            fi += 1

        mesh = mmdpy_mesh.mmdpyMesh(len(self.meshes), self.shader, new_vertex, new_face,
                                    data.materials[material_id],
                                    [self.bones[i] for i in new_bone_id if not i < 0])
        self.meshes.append(mesh)

        return True
