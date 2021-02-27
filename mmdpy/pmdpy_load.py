import struct
import os
from . import mmdpy_root


# #### #### PMD Loader #### ####
def load(self, filename):
    class empty:
        pass

    self.filename = filename
    self.path, self.ext = os.path.splitext(filename)
    self.directory = os.path.dirname(filename) + "/"

    try:
        fp = open(filename, "rb")
    except IOError:
        return False

    print("/**** **** **** **** Model File Informations **** **** **** ****/")

    # #### #### header #### ####
    head = struct.unpack_from("3s", fp.read(3))
    print(head[0])
    if head[0] != b"Pmd":
        return False

    version, model_name, comment = struct.unpack_from("f20s256s", fp.read(4 + 20 + 256))

    def str_to_hex(s):
        return [hex(ord(i))[2:4] for i in s]

    def padding_erase(_string, ps):
        end_point = 0
        bins = str_to_hex(_string)
        length = len(_string)
        while bins[end_point] != ps and end_point < length:
            end_point += 1
        return _string[:end_point]

    # Information
    self.version = version
    self.name = padding_erase(model_name.decode("cp932", "ignore"), 'f8')
    self.comment = padding_erase(comment.decode("cp932", "ignore"), 'f8')

    print(self.version)
    print(self.name)
    print(self.comment)

    # #### #### Data #### ####

    # #### #### Vertex #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    self.vertex = []
    for _ in range(loop_size):
        e = empty()
        e.ver = struct.unpack_from("3f", fp.read(12))
        e.nor = struct.unpack_from("3f", fp.read(12))
        e.uv = struct.unpack_from("2f", fp.read(8))
        e.bone_id = list(struct.unpack_from("2h", fp.read(4)))
        weight = ord(struct.unpack_from("c", fp.read(1))[0]) / 100.0
        e.bone_weight = [weight, 1 - weight]
        e.edge = (struct.unpack_from("c", fp.read(1))[0] != 0)

        self.vertex.append(e)

    # #### #### Face #### ####
    self.face_size = loop_size = struct.unpack_from("i", fp.read(4))[0]
    self.face = []
    for _ in range(0, loop_size, 3):
        self.face.append(struct.unpack_from("3h", fp.read(6)))

    # #### #### Material #### ####
    loop_size = struct.unpack_from("i", fp.read(4))[0]
    self.material = []
    for _ in range(loop_size):
        e = empty()

        e.diffuse = struct.unpack_from("3f", fp.read(12))
        e.alpha = struct.unpack_from("f", fp.read(4))[0]
        e.specularity = struct.unpack_from("f", fp.read(4))[0]
        e.specular_color = struct.unpack_from("3f", fp.read(12))
        e.mirror_color = struct.unpack_from("3f", fp.read(12))
        e.toon_index = ord(struct.unpack_from("c", fp.read(1))[0])
        e.edge = (struct.unpack_from("c", fp.read(1))[0] != 0)
        e.face_vert_count = struct.unpack_from("i", fp.read(4))[0]
        e.texture_name = struct.unpack_from("20s", fp.read(20))[0]

        self.material.append(e)

    # #### #### Bone #### ####
    loop_size = struct.unpack_from("h", fp.read(2))[0]
    self.bone = []
    for _ in range(loop_size):
        e = empty()

        e.name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
        e.parent_id = struct.unpack_from("h", fp.read(2))[0]
        e.tail_id = struct.unpack_from("h", fp.read(2))[0]
        e.bone_type = ord(struct.unpack_from("c", fp.read(1))[0])
        e.ik_parent_id = struct.unpack_from("h", fp.read(2))[0]
        e.position = struct.unpack_from("3f", fp.read(12))

        self.bone.append(e)

    # #### #### IK #### ####
    loop_size = struct.unpack_from("h", fp.read(2))[0]
    self.ik = []
    for _ in range(loop_size):
        e = empty()

        e.bone_id = struct.unpack_from("h", fp.read(2))[0]
        e.bone_to = struct.unpack_from("h", fp.read(2))[0]
        e.len = ord(struct.unpack_from("c", fp.read(1))[0])
        e.it = struct.unpack_from("h", fp.read(2))[0]
        e.weight = struct.unpack_from("f", fp.read(4))[0]
        e.child_bone_id = []
        for _ in range(e.len):
            c = struct.unpack_from("h", fp.read(2))[0]
            e.child_bone_id.append(c)

        self.ik.append(e)

    # #### #### Skin #### ####
    loop_size = struct.unpack_from("h", fp.read(2))[0]
    self.skin = []
    for _ in range(loop_size):
        e = empty()

        e.name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
        e.var_size = struct.unpack_from("i", fp.read(4))[0]
        e.type = ord(struct.unpack_from("c", fp.read(1))[0])
        e.var_id = []
        e.ver_offset = []
        for _ in range(e.var_size):
            t = struct.unpack_from("i", fp.read(4))[0]
            e.var_id.append(t)
            t = struct.unpack_from("3f", fp.read(12))
            e.ver_offset.append(t)

        self.skin.append(e)

    # #### #### Skin-Name #### ####
    loop_size = ord(struct.unpack_from("c", fp.read(1))[0])
    self.skin_name = []
    for _ in range(loop_size):
        self.skin_name.append(struct.unpack_from("h", fp.read(2))[0])

    # #### #### Bone-frame-Name #### ####
    loop_size = ord(struct.unpack_from("c", fp.read(1))[0])
    self.bone_frame_name = []
    for _ in range(loop_size):
        self.bone_frame_name.append(struct.unpack_from("50c", fp.read(50))[0])

    # #### #### Bone-Name #### ####
    loop_size = struct.unpack_from("h", fp.read(4))[0]
    self.bone_number = []
    for _ in range(loop_size):
        e = empty()

        e.id = struct.unpack_from("h", fp.read(2))[0]
        e.frame = ord(struct.unpack_from("c", fp.read(1))[0])

        self.bone_number.append(e)

    # #### #### English-header #### ####
    self.english_flag = (ord(struct.unpack_from("c", fp.read(1))[0]) != 0)
    if self.english_flag:
        self.english_head = {}
        en_model_name, en_comment = struct.unpack_from("20s256s", fp.read(20 + 256))
        self.english_head["name"] = padding_erase(en_model_name.decode("cp932", "ignore"), 'f8')
        self.english_head["comment"] = padding_erase(en_comment.decode("cp932", "ignore"), 'f8')

        print(self.english_head["name"])
        print(self.english_head["comment"])

        # bone name
        self.bone_name_eng = []
        for _ in range(len(self.bone)):
            en_name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
            self.bone_name_eng.append(en_name)

        # skin name
        self.skin_name_eng = []
        for _ in range(len(self.skin) - 1):
            en_name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
            self.skin_name_eng.append(en_name)

        # bone disp name
        self.bone_disp_name_eng = []
        for _ in range(len(self.bone_frame_name)):
            en_name = padding_erase(struct.unpack_from("50s", fp.read(50))[0].decode("cp932", "ignore"), 'f8')
            self.bone_disp_name_eng.append(en_name)

    # #### #### Toon-name #### ####
    self.toon_name = []
    for _ in range(10):
        name = struct.unpack_from("100s", fp.read(100))[0]
        self.toon_name.append(name)

    # #### #### Physics #### ####
    loop_size = struct.unpack_from("h", fp.read(4))[0]
    self.physics_flag = (loop_size > 0)
    self.physics = empty()
    self.physics.body = []
    self.physics.joint = []

    if self.physics_flag:
        # 剛体
        for _ in range(loop_size):
            name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
            bone_id = struct.unpack_from("h", fp.read(2))[0]
            group_id = ord(struct.unpack_from("c", fp.read(1))[0])
            group_mask = hex(struct.unpack_from("h", fp.read(2))[0])
            type_id = ord(struct.unpack_from("c", fp.read(1))[0])
            sizes = struct.unpack_from("3f", fp.read(12))
            pos = struct.unpack_from("3f", fp.read(12))
            rot = struct.unpack_from("3f", fp.read(12))
            mass = struct.unpack_from("f", fp.read(4))[0]
            pos_dim = struct.unpack_from("f", fp.read(4))[0]
            rot_dim = struct.unpack_from("f", fp.read(4))[0]
            recoil = struct.unpack_from("f", fp.read(4))[0]
            friction = struct.unpack_from("f", fp.read(4))[0]
            calc = ord(struct.unpack_from("c", fp.read(1))[0])

            e = empty()

            e.name = name
            e.bone_id = bone_id
            e.group_id = group_id
            e.group_mask = group_mask
            e.type_id = type_id

            e.sizes = empty()
            e.sizes.x = sizes[0]
            e.sizes.y = sizes[1]
            e.sizes.z = sizes[2]

            e.pos = pos
            e.rot = rot
            e.mass = mass
            e.pos_dim = pos_dim
            e.rot_dim = rot_dim
            e.recoil = recoil
            e.friction = friction
            e.calc = calc  # 0:固定剛体, 1:物理演算, 2:追従

            self.physics.body.append(e)

        # ジョイント
        loop_size = struct.unpack_from("h", fp.read(4))[0]
        for _ in range(loop_size):
            name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
            rigidbody_a = struct.unpack_from("i", fp.read(4))[0]
            rigidbody_b = struct.unpack_from("i", fp.read(4))[0]

            pos = struct.unpack_from("3f", fp.read(12))
            rot = struct.unpack_from("3f", fp.read(12))

            constrain_pos_1 = struct.unpack_from("3f", fp.read(12))
            constrain_pos_2 = struct.unpack_from("3f", fp.read(12))
            constrain_pos_3 = struct.unpack_from("3f", fp.read(12))
            constrain_pos_4 = struct.unpack_from("3f", fp.read(12))

            spring_pos = struct.unpack_from("3f", fp.read(12))
            spring_rot = struct.unpack_from("3f", fp.read(12))

            e = empty()

            e.name = name
            e.rigidbody_a = rigidbody_a
            e.rigidbody_b = rigidbody_b
            e.pos = pos
            e.rot = rot
            e.constrain_pos = [constrain_pos_1, constrain_pos_2, constrain_pos_3, constrain_pos_4]
            e.spring_pos = spring_pos
            e.spring_rot = spring_rot

            self.physics.joint.append(e)

    return True
