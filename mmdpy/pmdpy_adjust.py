
import struct
import os
import types
import numpy as np
from . import mmdpy_root
from . import mmdpy_texture


# #### #### PMD Adjuster #### ####
def adjust(self):
    class empty:
        pass

    # #### #### Vertex #### ####
    # 複数形は加工データ
    self.vertices = []
    for vv in self.vertex:
        v = empty()
        v.ver = vv.ver
        v.nor = vv.nor
        v.uv  = vv.uv
        v.bone_id = vv.bone_id + [0, 0]
        v.bone_weight = vv.bone_weight + [0, 0]
        v.edge = vv.edge

        self.vertices.append(v)

    # #### #### Face #### ####
    self.faces = self.face

    # #### #### Material #### ####
    self.materials = []
    m_top = 0
    for mm in self.material:
        m = mm

        m.top = m_top
        m.size = mm.face_vert_count
        m_top += m.size

        m.texture_name = bytes([x for x in m.texture_name if x != 0x00 and x != 0xfd]).decode("cp932")
        if len(m.texture_name) > 0:
            if "*" in m.texture_name:
                m.texture_name = m.texture_name[:m.texture_name.find("*")]
            m.texture_name = self.directory + m.texture_name
            m.texture = mmdpy_texture.mmdpyTexture(m.texture_name)
        else:
            m.texture = None

        self.materials.append(m)

    # #### #### Bone #### ####
    self.bones = []
    for i, bb in enumerate(self.bone):
        b = bb
        b.id = i
        b.name = b.name.replace("\x00", "")
        b.weight = 1.00

        # 回転制御
        b.ik_rotatable_control = lambda b, axis, rot: b.rot(axis, rot)
        self.bones.append(b)

    # # 親の設定 IK, bone...
    # for b in self.bones:
    #     b.ik_parent = self.bones[b.ik_parent_id]

    # #### #### IK #### ####
    self.iks = []
    for i in self.ik:
        ik = i
        ik.bone_me = self.bones[i.bone_id]
        ik.bone_to = self.bones[i.bone_to]
        ik.child_bones = []
        for c in i.child_bone_id:
            self.bones[c].ik_rotatable_control = lambda b, axis, rot: (b.rot(axis, rot * b.weight))
            self.bones[c].ik = i
            ik.child_bones.append(self.bones[c])
        self.iks.append(ik)

    def knee_control(b, axis, rot):
        v = np.matmul(b.rot(axis, rot, update_flag=False), np.array([0, 0, 1, 1]))
        if v[1] < b.weight:
            return
        b.rot(axis, rot)
    for b in self.bones:
        ik = [ik for ik in self.iks if ik.bone_me.name == b.name]
        b.ik = None
        if len(ik) == 0:
            continue
        ik = ik[0]
        ikt = empty()
        ikt.bone_me = ik.bone_me
        ikt.bone_to = ik.bone_to
        ikt.len = ik.len
        ikt.it = ik.it
        ikt.weight = ik.weight
        ikt.child_bones = ik.child_bones
        b.ik = ikt

        for c in b.ik.child_bones:
            c.weight = ik.weight

    for b in self.bones:
        if "ひざ" in b.name:
            b.ik_rotatable_control = knee_control

    # #### #### Physics #### ####
    if self.physics_flag:
        for r in self.physics.body:
            r.bone = self.bone[r.bone_id]
            r.pos = np.array(r.bone.position) + np.array(r.pos)

    return True
