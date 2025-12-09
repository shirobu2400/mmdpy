
import numpy as np
import os
from . import mmdpy_texture
from . import mmdpy_type
from . import pmdpy_type
from typing import Any, cast


# #### #### PMD Adjuster #### ####
def adjust(pmd_data: pmdpy_type.pmdpyType) -> None | mmdpy_type.mmdpyTypeModel:

    adjust_data = mmdpy_type.mmdpyTypeModel()

    # #### #### Vertex #### ####
    # 複数形は加工データ
    for vv in pmd_data.vertex:
        v = mmdpy_type.mmdpyTypeVertex()
        v.ver = np.asarray(vv.ver)
        v.nor = np.asarray(vv.nor)
        v.uv = np.asarray(vv.uv)
        v.bone_id = np.asarray(list(vv.bone_id) + [0, 0])
        v.bone_weight = np.asarray(list(vv.bone_weight) + [0.00, 0.00])
        v.edge = vv.edge

        adjust_data.vertices.append(v)

    # #### #### Face #### ####
    adjust_data.faces = [list(f) for f in pmd_data.face]

    # #### #### Material #### ####
    m_top = 0
    for mm in pmd_data.material:
        m = mmdpy_type.mmdpyTypeMaterial()
        m.diffuse = np.asarray(mm.diffuse)
        m.alpha = cast(float, mm.alpha)
        m.specularity = np.asarray(mm.specularity)
        m.specular_color = np.asarray(mm.specular_color)
        m.mirror_color = np.asarray(mm.mirror_color)
        m.toon_index = mm.toon_index
        m.edge_size = float(mm.edge)
        m.face_vert_count = mm.face_vert_count

        m.top = m_top
        m.size = m.face_vert_count
        m_top += m.size

        m.texture = None
        texture_name = mm.texture_name
        m.texture_name = bytes([x for x in texture_name if x != 0x00 and x != 0xfd]).decode("cp932")
        if len(m.texture_name) > 0:
            if "*" in str(m.texture_name):
                m.texture_name = m.texture_name[:str(m.texture_name).find("*")]
            texture_path = os.path.join(pmd_data.directory, cast(str, m.texture_name))
            if os.name == "nt":
                texture_path = texture_path.replace('/', '\\')
            m.texture = mmdpy_texture.mmdpyTexture(texture_path)
        m.both_side_flag = (mm.alpha < 1 - 1e-8)
        m.color = np.array(list(m.diffuse) + [m.alpha])
        if m.texture is not None:
            m.color[3] = 0

        adjust_data.materials.append(m)

    # #### #### Bone #### ####
    for i, bb in enumerate(pmd_data.bone):
        b = mmdpy_type.mmdpyTypeBone()
        b.id = i
        b.bone_type = bb.bone_type
        b.parent_id = bb.parent_id
        b.tail_id = bb.tail_id
        b.ik_parent_id = bb.ik_parent_id
        b.position = np.asarray(bb.position)
        b.name = bb.name.replace("\x00", "")
        b.weight = 1.00
        b.rotatable_control = lambda b, axis, rot: b.rot(axis, rot * b.weight)
        b.ik = None
        adjust_data.bones.append(b)

    # #### #### IK #### ####
    for pmd_ik in pmd_data.ik:
        mmd_ik = mmdpy_type.mmdpyTypeIK()

        mmd_ik.bone_index = pmd_ik.bone_id
        mmd_ik.bone_effect_index = pmd_ik.bone_to
        mmd_ik.length = pmd_ik.length
        mmd_ik.iteration = pmd_ik.iteration
        mmd_ik.weight = np.asarray([pmd_ik.weight, 0, 0, 0])
        mmd_ik.child_bones_index = pmd_ik.child_bone_id
        for c in mmd_ik.child_bones_index:
            adjust_data.bones[c].weight = pmd_ik.weight
            adjust_data.bones[c].rotatable_control = lambda b, axis, rot: b.rot(axis, rot * b.weight)

        adjust_data.bones[mmd_ik.bone_index].ik = mmd_ik

    # ひざの処理
    def knee_control(b: Any, axis: np.ndarray, rot: np.ndarray) -> None:
        v = np.matmul(b.rot(axis, rot, update_flag=False), np.array([0, 0, 1, 1]))
        if v[1] > 1e-4:
            return
        b.rot(axis, rot)

    for bone in adjust_data.bones:
        if "ひざ" in bone.name:
            bone.rotatable_control = knee_control

    # #### #### Physics #### ####
    adjust_data.physics_flag = pmd_data.physics_flag
    if pmd_data.physics_flag and pmd_data.physics is not None:
        adjust_data.physics = mmdpy_type.mmdpyTypePhysics()
        adjust_data.physics.body = []
        adjust_data.physics.joint = []

        if pmd_data.physics.body is not None:
            for pmd_body in pmd_data.physics.body:
                body = mmdpy_type.mmdpyTypePhysicsBody()

                bone_position = pmd_data.bone[pmd_body.bone_id].position
                body_pos = np.array(bone_position) + np.array(pmd_body.pos)
                # body_pos = np.array(pmd_body.pos)

                body.bone_id = pmd_body.bone_id
                body.name = pmd_body.name
                body.group_id = pmd_body.group_id
                body.group_mask = pmd_body.group_mask
                body.type_id = pmd_body.type_id
                body.sizes = np.asarray([pmd_body.sizes.x, pmd_body.sizes.y, pmd_body.sizes.z])
                body.pos = np.asarray(body_pos)
                body.rot = np.asarray(pmd_body.rot)
                body.mass = pmd_body.mass
                body.pos_dim = pmd_body.pos_dim
                body.rot_dim = pmd_body.rot_dim
                body.recoil = pmd_body.recoil
                body.friction = pmd_body.friction
                body.calc = pmd_body.calc

                adjust_data.physics.body.append(body)

        if pmd_data.physics.joint is not None:
            for pmd_joint in pmd_data.physics.joint:
                joint = mmdpy_type.mmdpyTypePhysicsJoint()

                joint.name = pmd_joint.name
                joint.rigidbody_a = pmd_joint.rigidbody_a
                joint.rigidbody_b = pmd_joint.rigidbody_b

                joint.pos = np.asarray(pmd_joint.pos)
                joint.rot = np.asarray(pmd_joint.rot)
                joint.constrain_pos = [np.asarray(x) for x in pmd_joint.constrain_pos]
                joint.spring_pos = np.asarray(pmd_joint.spring_pos)
                joint.spring_rot = np.asarray(pmd_joint.spring_rot)

                adjust_data.physics.joint.append(joint)

    return adjust_data
