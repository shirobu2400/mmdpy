import struct
import os
from typing import Tuple, List, Union, cast
from . import pmxpy_type
import numpy as np


# #### #### PMX Loader #### ####
def load(filename: str) -> Union[None, pmxpy_type.pmxpyType]:
    data = pmxpy_type.pmxpyType()

    data.filename = filename
    data.path, data.ext = os.path.splitext(filename)
    data.directory = os.path.dirname(filename) + "/"

    try:
        fp = open(filename, "rb")
    except IOError:
        return None

    print("/**** **** **** **** Model File Informations **** **** **** ****/")

    # #### #### header #### ####
    head = struct.unpack_from("4s", fp.read(4))[0]
    if head != b"Pmx " and head != b"PMX ":
        return None

    # Information
    version = struct.unpack_from("f", fp.read(4))[0]
    byte_size = ord(struct.unpack_from("c", fp.read(1))[0])
    header_byte = struct.unpack_from("{}c".format(byte_size), fp.read(byte_size))
    """
        バイト列 - byte
        [0] - エンコード方式  | 0:UTF16 1:UTF8
        [1] - 追加UV数 	| 0～4 詳細は頂点参照
        [2] - 頂点Indexサイズ | 1,2,4 のいずれか
        [3] - テクスチャIndexサイズ | 1,2,4 のいずれか
        [4] - 材質Indexサイズ | 1,2,4 のいずれか
        [5] - ボーンIndexサイズ | 1,2,4 のいずれか
        [6] - モーフIndexサイズ | 1,2,4 のいずれか
        [7] - 剛体Indexサイズ | 1,2,4 のいずれか
    """
    index_sizeof_list = {1: "b", 2: "h", 4: "i"}
    data.encode_type = ("utf-8" if header_byte[0] == 1 else "utf-16")
    data.add_uv_flag = bool(header_byte[1] == 1)
    data.face_index_sizeof = ord(header_byte[2])
    data.texture_index_sizeof = ord(header_byte[3])
    data.material_index_sizeof = ord(header_byte[4])
    data.bone_index_sizeof = ord(header_byte[5])
    data.morph_index_sizeof = ord(header_byte[6])
    data.rigidbody_index_sizeof = ord(header_byte[7])

    comment_length = struct.unpack_from("i", fp.read(4))[0]
    comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
    data.name = comment_bytes.decode(data.encode_type)

    comment_length = struct.unpack_from("i", fp.read(4))[0]
    comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
    data.name_eng = comment_bytes.decode(data.encode_type)

    comment_length = struct.unpack_from("i", fp.read(4))[0]
    comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
    data.comment = comment_bytes.decode(data.encode_type)

    comment_length = struct.unpack_from("i", fp.read(4))[0]
    comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
    data.comment_eng = comment_bytes.decode(data.encode_type)

    print("version:", version)
    print("encode:", data.encode_type)
    print("name:", data.name)
    print("name-eng:", data.name_eng)
    print("comment:", data.comment)
    print("comment-eng:", data.comment_eng)

    # #### #### Data #### ####

    # #### #### Vertex #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.vertex = []
    for _ in range(loop_size):
        vertex = pmxpy_type.pmxpyTypeLoadVertex()
        vertex.ver = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        vertex.nor = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        vertex.uv = cast(Tuple[float, float], struct.unpack_from("2f", fp.read(8)))
        vertex.add_uv = []

        if data.add_uv_flag:
            add_uv_size = 4
            vertex.add_uv = cast(List[float], struct.unpack_from("{}f".format(add_uv_size), fp.read(4 * add_uv_size)))

        vertex.weight_calc = ord(struct.unpack_from("c", fp.read(1))[0])
        vertex.bone_id = [0, 0, 0, 0]
        vertex.bone_weight = [0, 0, 0, 0]

        # BDEF1
        if vertex.weight_calc == 0:
            # n : ボーンIndexサイズ  | ウェイト1.0の単一ボーン(参照Index)
            vertex.bone_id[0] = struct.unpack_from(
                "{}".format(index_sizeof_list[data.bone_index_sizeof]),
                fp.read(data.bone_index_sizeof))[0]
            vertex.bone_weight[0] = 1.00

        # BDEF2
        if vertex.weight_calc == 1:
            # n : ボーンIndexサイズ  | ボーン1の参照Index
            # n : ボーンIndexサイズ  | ボーン2の参照Index
            # 4 : float             | ボーン1のウェイト値(0～1.0), ボーン2のウェイト値は 1.0-ボーン1ウェイト
            vertex.bone_id[0: 2] = cast(List[int],
                                        struct.unpack_from(
                                            "2{}".format(index_sizeof_list[data.bone_index_sizeof]),
                                            fp.read(2 * data.bone_index_sizeof)))
            vertex.bone_weight[0] = struct.unpack_from("f", fp.read(4))[0]
            vertex.bone_weight[1] = 1 - vertex.bone_weight[0]

        # BDEF4
        if vertex.weight_calc == 2:
            # n : ボーンIndexサイズ  | ボーン1の参照Index
            # n : ボーンIndexサイズ  | ボーン2の参照Index
            # n : ボーンIndexサイズ  | ボーン3の参照Index
            # n : ボーンIndexサイズ  | ボーン4の参照Index
            # 4 : float              | ボーン1のウェイト値
            # 4 : float              | ボーン2のウェイト値
            # 4 : float              | ボーン3のウェイト値
            # 4 : float              | ボーン4のウェイト値 (ウェイト計1.0の保障はない)
            vertex.bone_id = cast(List[int],
                                  struct.unpack_from(
                                      "4{}".format(index_sizeof_list[data.bone_index_sizeof]),
                                      fp.read(4 * data.bone_index_sizeof)))
            vertex.bone_weight = cast(List[float], struct.unpack_from("4f", fp.read(16)))

        # SDEF
        if vertex.weight_calc == 3:
            # n : ボーンIndexサイズ  | ボーン1の参照Index
            # n : ボーンIndexサイズ  | ボーン2の参照Index
            # 4 : float              | ボーン1のウェイト値(0～1.0), ボーン2のウェイト値は 1.0-ボーン1ウェイト
            # 12 : float3             | SDEF-C値(x,y,z)
            # 12 : float3             | SDEF-R0値(x,y,z)
            # 12 : float3             | SDEF-R1値(x,y,z) ※修正値を要計算
            vertex.bone_id[0: 2] = cast(List[int],
                                        struct.unpack_from(
                                            "2{}".format(index_sizeof_list[data.bone_index_sizeof]),
                                            fp.read(2 * data.bone_index_sizeof)))
            vertex.bone_weight[0] = struct.unpack_from("f", fp.read(4))[0]
            vertex.bone_weight[1] = 1 - vertex.bone_weight[0]
            vertex.sdef_options = cast(List[float], struct.unpack_from("9f", fp.read(36)))

        vertex.edge = struct.unpack_from("f", fp.read(4))[0]

        data.vertex.append(vertex)

    # #### #### Face #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.face = []
    for _ in range(0, loop_size, 3):
        x = cast(Tuple[int, int, int],
                 struct.unpack_from("3{}".format(index_sizeof_list[data.face_index_sizeof]),
                                    fp.read(3 * data.face_index_sizeof)))
        data.face.append(x)

    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.texture_name = []
    for _ in range(loop_size):
        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        texture_name = comment_bytes.decode(data.encode_type)
        data.texture_name.append(texture_name)

    # #### #### Material #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.material = []
    for _ in range(loop_size):
        material = pmxpy_type.pmxpyTypeLoadMaterial()

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        material.name = comment_bytes.decode(data.encode_type)

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        material.name_eng = comment_bytes.decode(data.encode_type)

        material.diffuse = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))
        material.specular_color = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        material.specular_scale = struct.unpack_from("f", fp.read(4))[0]
        material.ambient_color = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))

        material.bit_flag = struct.unpack_from("b", fp.read(1))[0]
        material.edge_color = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))
        material.edge_size = struct.unpack_from("f", fp.read(4))[0]

        material.texture_index = cast(int, struct.unpack_from(
            "{}".format(index_sizeof_list[data.texture_index_sizeof]), fp.read(data.texture_index_sizeof))[0])
        material.sphere_texture_index = cast(int, struct.unpack_from(
            "{}".format(index_sizeof_list[data.texture_index_sizeof]), fp.read(data.texture_index_sizeof))[0])

        material.sphere_mode = struct.unpack_from("b", fp.read(1))[0]
        material.toon_flag = (struct.unpack_from("b", fp.read(1))[0] != 0)

        material.texrure_name = ""
        if material.toon_flag:
            material.toon_texture_number = struct.unpack_from("b", fp.read(1))[0]
            material.texrure_name = "toon{:02d}.bmp".format(material.toon_texture_number + 1)
        else:
            material.toon_texture_number = struct.unpack_from(
                "{}".format(index_sizeof_list[data.texture_index_sizeof]), fp.read(data.texture_index_sizeof))[0]
            # if material.toon_texture_number < len(data.texture_name):
            #     material.texrure_name = data.texture_name[material.toon_texture_number]
            if material.texture_index < len(data.texture_name):
                material.texrure_name = data.texture_name[material.texture_index]

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        material.comment = comment_bytes.decode(data.encode_type)

        material.face_vert_count = struct.unpack_from("i", fp.read(4))[0]

        data.material.append(material)

    # #### #### Bone #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.bone = []
    for _ in range(loop_size):
        bone = pmxpy_type.pmxpyTypeLoadBone()

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        bone.name = comment_bytes.decode(data.encode_type)

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        bone.name_eng = comment_bytes.decode(data.encode_type)

        bone.position = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
        bone.parent_id = cast(int, struct.unpack_from(
            "{}".format(index_sizeof_list[data.bone_index_sizeof]), fp.read(data.bone_index_sizeof))[0])
        bone.level = struct.unpack_from("i", fp.read(4))[0]
        bone.bone_flag = struct.unpack_from("h", fp.read(2))[0]

        if bone.bone_flag & 0x0001:
            # 接続先(PMD子ボーン指定)表示方法 -> 0:座標オフセットで指定 1:ボーンで指定
            bone.child_flag = True
            bone.child_index = cast(int, struct.unpack_from(
                "{}".format(index_sizeof_list[data.bone_index_sizeof]), fp.read(data.bone_index_sizeof))[0])
        else:
            bone.child_flag = False
            bone.offset_position = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))

        # 回転可能
        bone.rotation_flag = ((bone.bone_flag & 0x0002) != 0x0000)

        # 移動可能
        bone.translate_flag = ((bone.bone_flag & 0x0004) != 0x0000)

        # 表示
        bone.show_flag = ((bone.bone_flag & 0x0008) != 0x0000)

        # 操作可能
        bone.user_update_flag = ((bone.bone_flag & 0x0010) != 0x0000)

        # 回転付与
        bone.grant_rotation_flag = False
        if bone.bone_flag & 0x0100:
            bone.grant_rotation_flag = True
            bone.grant_rotation_index = cast(int, struct.unpack_from(
                                                    "{}".format(index_sizeof_list[data.bone_index_sizeof]),
                                                    fp.read(data.bone_index_sizeof))[0])
            bone.grant_rotation_rate = struct.unpack_from("f", fp.read(4))[0]

        # 移動付与
        bone.grant_translate_flag = False
        if bone.bone_flag & 0x0200:
            bone.grant_translate_flag = True
            bone.grant_translate_index = cast(int, struct.unpack_from(
                                                    "{}".format(index_sizeof_list[data.bone_index_sizeof]),
                                                    fp.read(data.bone_index_sizeof))[0])
            bone.grant_translate_rate = struct.unpack_from("f", fp.read(4))[0]

        # 軸固定
        bone.axis_vector = None
        if bone.bone_flag & 0x0400:
            bone.axis_vector = struct.unpack_from("3f", fp.read(12))[0]

        # ローカル軸
        bone.local_axis_flag = False
        if bone.bone_flag & 0x0800:
            bone.local_axis_flag = True
            bone.local_axis_x = struct.unpack_from("3f", fp.read(12))[0]
            bone.local_axis_z = struct.unpack_from("3f", fp.read(12))[0]

        # 物理後変形軸
        bone.physical_update_flag = ((bone.bone_flag & 0x1000) != 0x0000)

        # 外部親変形
        bone.outside_parent_update_flag = False
        if bone.bone_flag & 0x2000:
            bone.outside_parent_update_flag = True
            bone.outside_parent_update_key_value = struct.unpack_from("i", fp.read(4))[0]

        # IK
        bone.ik = None
        if bone.bone_flag & 0x0020:
            ik: pmxpy_type.pmxpyTypeLoadIK = pmxpy_type.pmxpyTypeLoadIK()
            ik.target_bone_index = cast(int,
                                        struct.unpack_from(
                                            "{}".format(index_sizeof_list[data.bone_index_sizeof]),
                                            fp.read(data.bone_index_sizeof))[0])
            ik.iteration = struct.unpack_from("i", fp.read(4))[0]
            ik.radius_range = struct.unpack_from("f", fp.read(4))[0]
            link_num = struct.unpack_from("i", fp.read(4))[0]
            ik.child_bone_id = []
            for _ in range(link_num):
                link: pmxpy_type.pmxpyTypeLoadIKLink = pmxpy_type.pmxpyTypeLoadIKLink()
                link.bone_id = cast(int,
                                    struct.unpack_from(
                                        "{}".format(index_sizeof_list[data.bone_index_sizeof]),
                                        fp.read(data.bone_index_sizeof))[0])
                link.rotate_limit_flag = (struct.unpack_from("b", fp.read(1))[0] != 0)
                if link.rotate_limit_flag:
                    link.btm = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
                    link.top = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
                ik.child_bone_id.append(link)
            bone.ik = ik

        data.bone.append(bone)

    # #### #### モーフ #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.morph = []
    uv_number = 0
    for _ in range(loop_size):
        morph = pmxpy_type.pmxpyTypeLoadMorph()

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        morph.name = comment_bytes.decode(data.encode_type)

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        morph.eng_name = comment_bytes.decode(data.encode_type)

        morph.panel = ord(struct.unpack_from("c", fp.read(1))[0])
        morph.type = ord(struct.unpack_from("c", fp.read(1))[0])
        morph.offset_num = struct.unpack_from("i", fp.read(4))[0]

        if morph.type == 1:
            morph.vertex = []
            for _ in range(morph.offset_num):
                v = pmxpy_type.pmxpyTypeLoadMorphVertex()
                v.vertex_id = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[data.face_index_sizeof]),
                    fp.read(data.face_index_sizeof))[0])
                v.vertex = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
                morph.vertex.append(v)
        if morph.type == 4:
            uv_number = 0
        if morph.type == 5:
            uv_number = 1
        if morph.type == 6:
            uv_number = 2
        if morph.type == 7:
            uv_number = 3
        if morph.type == 3:
            morph.uv = []
            for _ in range(morph.offset_num):
                u = pmxpy_type.pmxpyTypeLoadMorphUV()
                u.uv_number = uv_number
                u.uv_id = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[data.face_index_sizeof]),
                    fp.read(data.face_index_sizeof))[0])
                u.uv = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))
                morph.uv.append(u)
        if morph.type == 2:
            morph.bone = []
            for _ in range(morph.offset_num):
                b = pmxpy_type.pmxpyTypeLoadMorphBone()
                b.bone_id = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[data.bone_index_sizeof]),
                    fp.read(data.bone_index_sizeof))[0])
                b.translate = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
                b.rotation = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))
                morph.bone.append(b)
        if morph.type == 8:
            morph.material = []
            for _ in range(morph.offset_num):
                m = pmxpy_type.pmxpyTypeLoadMorphMaterial()
                m.material_id = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[data.material_index_sizeof]),
                    fp.read(data.material_index_sizeof))[0])
                m.calc_format = ord(struct.unpack_from("c", fp.read(1))[0])

                m.diffuse = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))
                m.specular = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
                m.specular_alpha = cast(float, struct.unpack_from("f", fp.read(4)))
                m.ambient = cast(Tuple[float, float, float], struct.unpack_from("3f", fp.read(12)))
                m.edge_color = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))
                m.edge_size = cast(float, struct.unpack_from("f", fp.read(4)))
                m.texture_alpha = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))
                m.sphere_alpha = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))
                m.toon_texture_alpha = cast(Tuple[float, float, float, float], struct.unpack_from("4f", fp.read(16)))

                morph.material.append(m)
        if morph.type == 0:
            morph.group = []
            for _ in range(morph.offset_num):
                g = pmxpy_type.pmxpyTypeLoadMorphGroup()
                g.grouo_id = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[data.morph_index_sizeof]),
                    fp.read(data.morph_index_sizeof))[0])
                g.morph_rate = cast(float, struct.unpack_from("f", fp.read(4)))
                morph.group.append(g)

        data.morph.append(morph)

    # #### #### 表示枠 #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.disp = []
    for _ in range(loop_size):
        d: pmxpy_type.pmxpyTypeLoadDispFrame = pmxpy_type.pmxpyTypeLoadDispFrame()

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        d.name = comment_bytes.decode(data.encode_type)

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        d.eng_name = comment_bytes.decode(data.encode_type)

        d.frame_flag = (ord(struct.unpack_from("c", fp.read(1))[0]) == 1)
        d.index_num = struct.unpack_from("i", fp.read(4))[0]

        d.indexs = []
        for _ in range(d.index_num):
            s: pmxpy_type.pmxpyTypeLoadDispFrameInline = pmxpy_type.pmxpyTypeLoadDispFrameInline()
            s.index = ord(struct.unpack_from("c", fp.read(1))[0])
            index_size = data.bone_index_sizeof
            if s.index:
                index_size = data.morph_index_sizeof
            s.index = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[index_size]),
                    fp.read(index_size))[0])
            d.indexs.append(s)
        data.disp.append(d)

    # #### #### 剛体 #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.physics_flag = (loop_size > 0)
    data.physics = pmxpy_type.pmdpyLoadPhysics()
    data.physics.body = []
    for _ in range(loop_size):
        p: pmxpy_type.pmxpyTypeLoadPhysicsBody = pmxpy_type.pmxpyTypeLoadPhysicsBody()

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        p.name = comment_bytes.decode(data.encode_type)

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        p.eng_name = comment_bytes.decode(data.encode_type)

        p.bone_id = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[data.bone_index_sizeof]),
                    fp.read(data.bone_index_sizeof))[0])
        p.group_id = ord(struct.unpack_from("c", fp.read(1))[0])
        p.not_touch_group_flag = struct.unpack_from("h", fp.read(2))[0]

        p.type_id = ord(struct.unpack_from("c", fp.read(1))[0])
        p.sizes = np.asarray(struct.unpack_from("3f", fp.read(12)))

        p.pos = np.asarray(struct.unpack_from("3f", fp.read(12)))
        p.rot = np.asarray(struct.unpack_from("3f", fp.read(12)))

        p.mass = struct.unpack_from("f", fp.read(4))[0]
        p.ac_t = struct.unpack_from("f", fp.read(4))[0]
        p.ac_r = struct.unpack_from("f", fp.read(4))[0]

        p.repulsion = struct.unpack_from("f", fp.read(4))[0]
        p.friction = struct.unpack_from("f", fp.read(4))[0]

        p.rigidbody_type = ord(struct.unpack_from("c", fp.read(1))[0])

        data.physics.body.append(p)

    # #### #### ジョイント #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    data.physics.joint = []
    for _ in range(loop_size):
        j: pmxpy_type.pmxpyTypeLoadPhysicsJoint = pmxpy_type.pmxpyTypeLoadPhysicsJoint()

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        j.name = comment_bytes.decode(data.encode_type)

        comment_length = struct.unpack_from("i", fp.read(4))[0]
        comment_bytes = bytes(struct.unpack_from("{}s".format(comment_length), fp.read(comment_length))[0])
        j.eng_name = comment_bytes.decode(data.encode_type)

        j.type = ord(struct.unpack_from("c", fp.read(1))[0])

        if j.type != 0:
            continue

        j.a_index = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[data.rigidbody_index_sizeof]),
                    fp.read(data.rigidbody_index_sizeof))[0])
        j.b_index = cast(int, struct.unpack_from(
                    "{}".format(index_sizeof_list[data.rigidbody_index_sizeof]),
                    fp.read(data.rigidbody_index_sizeof))[0])

        j.pos = np.asarray(struct.unpack_from("3f", fp.read(12)))
        j.rot = np.asarray(struct.unpack_from("3f", fp.read(12)))

        j.trans_limit1 = np.asarray(struct.unpack_from("3f", fp.read(12)))
        j.trans_limit2 = np.asarray(struct.unpack_from("3f", fp.read(12)))

        j.rot_limit1 = np.asarray(struct.unpack_from("3f", fp.read(12)))
        j.rot_limit2 = np.asarray(struct.unpack_from("3f", fp.read(12)))

        j.spring_pos = np.asarray(struct.unpack_from("3f", fp.read(12)))
        j.spring_rot = np.asarray(struct.unpack_from("3f", fp.read(12)))
        j.spring_rot = np.array([r * np.pi / 180.0 for r in j.spring_rot])

        data.physics.joint.append(j)

    fp.close()
    return data
