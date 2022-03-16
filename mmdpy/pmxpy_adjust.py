
import numpy as np
import os
from . import mmdpy_texture
from . import mmdpy_type
from . import pmxpy_type
from typing import Any, cast, Union, Dict


# #### #### PMD Adjuster #### ####
def adjust(pmx_data: pmxpy_type.pmxpyType) -> Union[None, mmdpy_type.mmdpyTypeModel]:

    adjust_data = mmdpy_type.mmdpyTypeModel()

    # #### #### Vertex #### ####
    # 複数形は加工データ
    for vv in pmx_data.vertex:
        v = mmdpy_type.mmdpyTypeVertex()
        v.ver = np.asarray(vv.ver)
        v.nor = np.asarray(vv.nor)
        v.uv = np.asarray(vv.uv)
        v.bone_id = np.asarray(vv.bone_id)
        v.bone_weight = np.asarray(vv.bone_weight)
        v.edge = vv.edge

        adjust_data.vertices.append(v)

    # #### #### Face #### ####
    adjust_data.faces = [list(f) for f in pmx_data.face]

    # #### #### Material #### ####
    m_top = 0
    for mm in pmx_data.material:
        m = mmdpy_type.mmdpyTypeMaterial()
        m.diffuse = np.array(mm.diffuse)
        m.alpha = 1.00  # cast(float, mm.specular_scale)
        m.specularity = np.array(mm.specular_color)
        m.specular_color = np.array(mm.specular_color)
        m.mirror_color = np.array(mm.ambient_color)
        m.toon_index = mm.texture_index
        m.edge_size = mm.edge_size
        m.face_vert_count = mm.face_vert_count

        m.top = m_top
        m.size = m.face_vert_count
        m_top += m.size

        loaded_textures: Dict[str, mmdpy_texture.mmdpyTexture] = {}
        m.texture = None
        m.texture_name = mm.texrure_name
        if len(m.texture_name) > 0:
            if "*" in str(m.texture_name):
                m.texture_name = m.texture_name[:str(m.texture_name).find("*")]
            texture_path = os.path.join(pmx_data.directory, cast(str, m.texture_name))

            if texture_path not in loaded_textures.keys():
                loaded_textures[texture_path] = mmdpy_texture.mmdpyTexture(texture_path)
            m.texture = loaded_textures[texture_path]
        m.both_side_flag = ((mm.bit_flag & 0x01) != 0x00)
        m.color = m.diffuse
        if m.texture is not None:
            m.color[3] = 0.00

        adjust_data.materials.append(m)

    # #### #### Bone #### ####
    for i, bb in enumerate(pmx_data.bone):
        b = mmdpy_type.mmdpyTypeBone()
        b.id = i
        b.level = bb.level  # 実行順の階層
        b.parent_id = bb.parent_id
        b.position = np.asarray(bb.position)
        b.name = bb.name.replace("\x00", "")
        b.weight = 1.00
        b.rotatable_control = lambda b, axis, rot: b.rot(axis, rot * b.weight)

        # IK処理
        b.ik = None
        if bb.ik:
            ik = mmdpy_type.mmdpyTypeIK()
            ik.bone_index = int(i)
            ik.bone_effect_index = bb.ik.target_bone_index
            ik.iteration = bb.ik.iteration
            ik.child_bones_index = [c.bone_id for c in bb.ik.child_bone_id]
            b.ik = ik

        adjust_data.bones.append(b)

    # 付与親の処理
    for b, bb in zip(adjust_data.bones, pmx_data.bone):
        b.grant_rotation_parent_bone_index = None
        b.grant_translate_parent_bone_index = None

        if bb.grant_rotation_flag:
            b.grant_rotation_parent_bone_index = bb.grant_rotation_index
            b.grant_rotation_parent_rate = bb.grant_rotation_rate

        if bb.grant_translate_flag:
            b.grant_translate_parent_bone_index = bb.grant_translate_index
            b.grant_translate_parent_rate = bb.grant_translate_rate

    # # #### #### IK #### ####
    # for pmd_ik in pmx_data.ik:
    #     mmd_ik = mmdpy_type.mmdpyTypeIK()

    #     mmd_ik.bone_index = pmd_ik.bone_id
    #     mmd_ik.bone_effect_index = pmd_ik.bone_to
    #     mmd_ik.length = pmd_ik.length
    #     mmd_ik.iteration = pmd_ik.iteration
    #     mmd_ik.weight = np.asarray([pmd_ik.weight, 0, 0, 0])
    #     mmd_ik.child_bones_index = pmd_ik.child_bone_id
    #     for c in mmd_ik.child_bones_index:
    #         adjust_data.bones[c].weight = pmd_ik.weight
    #         adjust_data.bones[c].rotatable_control = lambda b, axis, rot: b.rot(axis, rot * b.weight)

    #     adjust_data.iks.append(mmd_ik)

    # ひざの処理
    def knee_control(b: Any, axis: np.ndarray, rot: np.ndarray) -> None:
        v = np.matmul(b.rot(axis, rot, update_flag=False), np.array([0, 0, 1, 1]))
        if v[1] > 1e-4:
            return
        b.rot(axis, rot)

    for bone in adjust_data.bones:
        if "ひざ" in bone.name:
            bone.rotatable_control = knee_control

    # # #### #### Physics #### ####
    adjust_data.physics_flag = pmx_data.physics_flag
    if pmx_data.physics_flag and pmx_data.physics is not None:
        adjust_data.physics = mmdpy_type.mmdpyTypePhysics()
        adjust_data.physics.body = []
        adjust_data.physics.joint = []

        if pmx_data.physics.body is not None:
            for pmx_body in pmx_data.physics.body:
                body = mmdpy_type.mmdpyTypePhysicsBody()

                bone_position = pmx_data.bone[pmx_body.bone_id].position
                body_pos = np.array(bone_position) + np.array(pmx_body.pos)
                # body_pos = np.array(pmd_body.pos)

                body.bone_id = pmx_body.bone_id
                body.name = pmx_body.name
                body.group_id = pmx_body.group_id
                body.group_mask = pmx_body.not_touch_group_flag
                body.type_id = pmx_body.type_id
                body.sizes = np.asarray([pmx_body.sizes[0], pmx_body.sizes[1], pmx_body.sizes[2]])
                body.pos = np.asarray(body_pos)
                body.rot = np.asarray(pmx_body.rot)
                body.mass = pmx_body.mass
                # body.pos_dim = pmx_body.pos
                # body.rot_dim = pmx_body.rot
                body.recoil = pmx_body.repulsion
                body.friction = pmx_body.friction
                body.calc = pmx_body.rigidbody_type

                adjust_data.physics.body.append(body)

        if pmx_data.physics.joint is not None:
            for pmx_joint in pmx_data.physics.joint:
                joint = mmdpy_type.mmdpyTypePhysicsJoint()

                joint.name = pmx_joint.name
                joint.rigidbody_a = pmx_joint.a_index
                joint.rigidbody_b = pmx_joint.b_index

                joint.pos = np.asarray(pmx_joint.pos)
                joint.rot = np.asarray(pmx_joint.rot)
                # joint.constrain_pos = [np.asarray(x) for x in pmx_joint.constrain_pos]
                joint.spring_pos = np.asarray(pmx_joint.spring_pos)
                joint.spring_rot = np.asarray(pmx_joint.spring_rot)

                adjust_data.physics.joint.append(joint)

    return adjust_data
