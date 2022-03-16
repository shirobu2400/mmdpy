import struct
import os
from typing import Tuple, List, Union, cast
from . import pmdpy_type


# #### #### PMD Loader #### ####
def load(filename: str) -> Union[None, pmdpy_type.pmdpyType]:
    data = pmdpy_type.pmdpyType()

    data.filename = filename
    data.path, data.ext = os.path.splitext(filename)
    data.directory = os.path.dirname(filename) + "/"

    try:
        fp = open(filename, "rb")
    except IOError:
        return None

    print("/**** **** **** **** Model File Informations **** **** **** ****/")

    # #### #### header #### ####
    head = struct.unpack_from("3s", fp.read(3))
    print(head[0])
    if head[0] != b"Pmd":
        return None

    version, model_name, comment = struct.unpack_from("f20s256s", fp.read(4 + 20 + 256))

    def str_to_hex(s) -> List[str]:
        return [hex(ord(i))[2:4] for i in s]

    def padding_erase(_string, ps) -> str:
        end_point = 0
        bins = str_to_hex(_string)
        length = len(_string)
        while bins[end_point] != ps and end_point < length:
            end_point += 1
        return _string[:end_point]

    # Information
    data.version = version
    data.name = padding_erase(model_name.decode("cp932", "ignore"), 'f8')
    data.comment = padding_erase(comment.decode("cp932", "ignore"), 'f8')

    print(data.version)
    print(data.name)
    print(data.comment)

    # #### #### Data #### ####

    # #### #### Vertex #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.vertex = []
    for _ in range(loop_size):
        vertex = pmdpy_type.pmdpyTypeLoadVertex()
        vertex.ver = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        vertex.nor = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        vertex.uv = cast(Tuple[float, float], struct.unpack_from("2f", fp.read(8)))
        vertex.bone_id = cast(Tuple[int, int], struct.unpack_from("2h", fp.read(4)))
        weight = cast(float, ord(struct.unpack_from("c", fp.read(1))[0]) / 100.0)
        vertex.bone_weight = (weight, 1 - weight)
        vertex.edge = (struct.unpack_from("c", fp.read(1))[0] != 0)

        data.vertex.append(vertex)

    # #### #### Face #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]

    data.face = []
    for _ in range(0, loop_size, 3):
        x = cast(Tuple[int, int, int], struct.unpack_from("3h", fp.read(6)))
        data.face.append(x)

    # #### #### Material #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.material = []
    for _ in range(loop_size):
        material = pmdpy_type.pmdpyTypeLoadMaterial()

        material.diffuse = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        material.alpha = cast(float, struct.unpack_from("f", fp.read(4))[0])
        material.specularity = struct.unpack_from("f", fp.read(4))[0]
        material.specular_color = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        material.mirror_color = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        material.toon_index = ord(struct.unpack_from("c", fp.read(1))[0])
        material.edge = (struct.unpack_from("c", fp.read(1))[0] != 0)
        material.face_vert_count = struct.unpack_from("i", fp.read(4))[0]
        material.texture_name = bytes(struct.unpack_from("20s", fp.read(20))[0])

        data.material.append(material)

    # #### #### Bone #### ####
    loop_size = struct.unpack_from("h", fp.read(2))[0]
    data.bone = []
    for _ in range(loop_size):
        bone = pmdpy_type.pmdpyTypeLoadBone()

        bone.name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
        bone.parent_id = cast(int, struct.unpack_from("h", fp.read(2))[0])
        bone.tail_id = cast(int, struct.unpack_from("h", fp.read(2))[0])
        bone.bone_type = ord(struct.unpack_from("c", fp.read(1))[0])
        bone.ik_parent_id = cast(int, struct.unpack_from("h", fp.read(2))[0])
        bone.position = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))

        data.bone.append(bone)

    # #### #### IK #### ####
    loop_size = struct.unpack_from("h", fp.read(2))[0]
    data.ik = []
    for _ in range(loop_size):
        ik = pmdpy_type.pmdpyTypeLoadIK()

        ik.bone_id = cast(int, struct.unpack_from("h", fp.read(2))[0])
        ik.bone_to = cast(int, struct.unpack_from("h", fp.read(2))[0])
        ik.length = ord(struct.unpack_from("c", fp.read(1))[0])
        ik.iteration = cast(int, struct.unpack_from("h", fp.read(2))[0])
        ik.weight = cast(float, struct.unpack_from("f", fp.read(4))[0])
        ik.child_bone_id = []
        for _ in range(ik.length):
            c = cast(int, struct.unpack_from("h", fp.read(2))[0])
            ik.child_bone_id.append(c)

        data.ik.append(ik)

    # #### #### Skin #### ####
    loop_size = struct.unpack_from("h", fp.read(2))[0]
    data.skin = []
    for _ in range(loop_size):
        skin = pmdpy_type.pmdpyTypeLoadSkin()

        skin.name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
        skin.var_size = cast(int, struct.unpack_from("i", fp.read(4))[0])
        skin.type = ord(struct.unpack_from("c", fp.read(1))[0])
        skin.var_id = []
        skin.ver_offset = []
        for _ in range(skin.var_size):
            t = cast(int, struct.unpack_from("i", fp.read(4))[0])
            skin.var_id.append(t)
            v = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            skin.ver_offset.append(v)

        data.skin.append(skin)

    # #### #### Skin-Name #### ####
    loop_size = ord(struct.unpack_from("c", fp.read(1))[0])
    data.skin_name = []
    for _ in range(loop_size):
        skin_name_index = cast(int, struct.unpack_from("h", fp.read(2))[0])
        data.skin_name.append(skin_name_index)

    # #### #### Bone-frame-Name #### ####
    loop_size = ord(struct.unpack_from("c", fp.read(1))[0])
    data.bone_frame_name = []
    for _ in range(loop_size):
        bone_frame_name = cast(str, struct.unpack_from("50c", fp.read(50))[0])
        data.bone_frame_name.append(bone_frame_name)

    # #### #### Bone-Name #### ####
    loop_size = struct.unpack_from("h", fp.read(4))[0]
    data.bone_number = []
    for _ in range(loop_size):
        bonename = pmdpy_type.pmdpyTypeLoadBoneName()

        bonename.id = cast(int, struct.unpack_from("h", fp.read(2))[0])
        bonename.frame = ord(struct.unpack_from("c", fp.read(1))[0])

        data.bone_number.append(bonename)

    # #### #### English-header #### ####
    data.english_flag = (ord(struct.unpack_from("c", fp.read(1))[0]) != 0)
    if data.english_flag:
        data.english_head = {}
        en_model_name, en_comment = struct.unpack_from("20s256s", fp.read(20 + 256))
        data.english_head["name"] = padding_erase(en_model_name.decode("cp932", "ignore"), 'f8')
        data.english_head["comment"] = padding_erase(en_comment.decode("cp932", "ignore"), 'f8')

        print(data.english_head["name"])
        print(data.english_head["comment"])

        # bone name
        data.bone_name_eng = []
        for _ in range(len(data.bone)):
            en_name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
            data.bone_name_eng.append(en_name)

        # skin name
        data.skin_name_eng = []
        for _ in range(len(data.skin) - 1):
            en_name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
            data.skin_name_eng.append(en_name)

        # bone disp name
        data.bone_disp_name_eng = []
        for _ in range(len(data.bone_frame_name)):
            en_name = padding_erase(struct.unpack_from("50s", fp.read(50))[0].decode("cp932", "ignore"), 'f8')
            data.bone_disp_name_eng.append(en_name)

    # #### #### Toon-name #### ####
    data.toon_name = []
    for _ in range(10):
        name = struct.unpack_from("100s", fp.read(100))[0]
        data.toon_name.append(name)

    # #### #### Physics #### ####
    loop_size = struct.unpack_from("h", fp.read(4))[0]
    data.physics_flag = (loop_size > 0)
    data.physics = pmdpy_type.pmdpyLoadPhysics()
    data.physics.body = []
    data.physics.joint = []
    if data.physics_flag:
        # 剛体
        for _ in range(loop_size):
            name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
            bone_id = cast(int, struct.unpack_from("h", fp.read(2))[0])
            group_id = ord(struct.unpack_from("c", fp.read(1))[0])
            group_mask = hex(struct.unpack_from("h", fp.read(2))[0])
            type_id = ord(struct.unpack_from("c", fp.read(1))[0])
            sizes = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            pos = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            rot = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            mass = cast(float, struct.unpack_from("f", fp.read(4))[0])
            pos_dim = cast(float, struct.unpack_from("f", fp.read(4))[0])
            rot_dim = cast(float, struct.unpack_from("f", fp.read(4))[0])
            recoil = cast(float, struct.unpack_from("f", fp.read(4))[0])
            friction = cast(float, struct.unpack_from("f", fp.read(4))[0])
            calc = ord(struct.unpack_from("c", fp.read(1))[0])

            body = pmdpy_type.pmdpyTypeLoadPhysicsBody()

            body.name = name
            body.bone_id = bone_id
            body.group_id = group_id
            body.group_mask = group_mask
            body.type_id = type_id

            body.sizes = pmdpy_type.pmdpyTypeLoadPhysicsBodyVector()
            body.sizes.x = sizes[0]
            body.sizes.y = sizes[1]
            body.sizes.z = sizes[2]

            body.pos = pos
            body.rot = rot
            body.mass = mass
            body.pos_dim = pos_dim
            body.rot_dim = rot_dim
            body.recoil = recoil
            body.friction = friction
            body.calc = calc  # 0:固定剛体, 1:物理演算, 2:追従

            data.physics.body.append(body)

        # ジョイント
        loop_size = struct.unpack_from("h", fp.read(4))[0]
        for _ in range(loop_size):
            name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
            rigidbody_a = struct.unpack_from("i", fp.read(4))[0]
            rigidbody_b = struct.unpack_from("i", fp.read(4))[0]

            pos = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            rot = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))

            constrain_pos_1 = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            constrain_pos_2 = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            constrain_pos_3 = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            constrain_pos_4 = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))

            spring_pos = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
            spring_rot = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))

            joint = pmdpy_type.pmdpyTypeLoadPhysicsJoint()

            joint.name = name
            joint.rigidbody_a = rigidbody_a
            joint.rigidbody_b = rigidbody_b
            joint.pos = pos
            joint.rot = rot
            joint.constrain_pos = [constrain_pos_1, constrain_pos_2, constrain_pos_3, constrain_pos_4]
            joint.spring_pos = spring_pos
            joint.spring_rot = spring_rot

            data.physics.joint.append(joint)

    fp.close()
    return data
