import struct
import os
import mmdpy_root


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
        e.uv  = struct.unpack_from("2f", fp.read(8))
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

        e.diffuse               = struct.unpack_from("3f", fp.read(12))
        e.alpha                 = struct.unpack_from("f", fp.read(4))[0]
        e.specularity           = struct.unpack_from("f", fp.read(4))[0]
        e.specular_color        = struct.unpack_from("3f", fp.read(12))
        e.mirror_color          = struct.unpack_from("3f", fp.read(12))
        e.toon_index            = ord(struct.unpack_from("c", fp.read(1))[0])
        e.edge                  = (struct.unpack_from("c", fp.read(1))[0] != 0)
        e.face_vert_count       = struct.unpack_from("i", fp.read(4))[0]
        e.texture_name          = struct.unpack_from("20s", fp.read(20))[0]

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

    # # #### #### Skin #### ####
    # self.skin_size = loop_size = struct.unpack_from("h", fp.read(2))[0]
    # self.skin = {"name": [], "ver_size": [], "type": [], "ver_id": [], "ver_offset": []}
    # for i in range(loop_size):
    #     self.skin["name"].append(padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8'))
    #     self.skin["ver_size"].append(struct.unpack_from("i", fp.read(4))[0])
    #     self.skin["type"].append(ord(struct.unpack_from("c", fp.read(1))[0]))
    #     ver_id = []
    #     ver_offset = []
    #     for j in range(self.skin["ver_size"][-1]):
    #         ver_id.append(struct.unpack_from("i", fp.read(4))[0])
    #         ver_offset.append(struct.unpack_from("3f", fp.read(12)))
    #     self.skin["ver_id"].append(ver_id)
    #     self.skin["ver_offset"].append(ver_offset)

    # # #### #### Skin-Name #### ####
    # self.skin_disp_size = loop_size = ord(struct.unpack_from("c", fp.read(1))[0])
    # self.skin_disp = {"id": []}
    # for i in range(loop_size):
    #     self.skin_disp["id"].append(struct.unpack_from("h", fp.read(2))[0])

    # # #### #### Bone-frame-Name #### ####
    # self.bone_disp_size = loop_size = ord(struct.unpack_from("c", fp.read(1))[0])
    # self.bone_disp = {"name": []}
    # for i in range(loop_size):
    #     self.bone_disp["name"].append(struct.unpack_from("50c", fp.read(50))[0])

    # # #### #### Bone-Name #### ####
    # self.bone_number_size = loop_size = struct.unpack_from("h", fp.read(4))[0]
    # self.bone_number = {"id": [], "frame_id": []}
    # for i in range(loop_size):
    #     self.bone_number["id"].append(struct.unpack_from("h", fp.read(2))[0])
    #     self.bone_number["frame_id"].append(ord(struct.unpack_from("c", fp.read(1))[0]))

    # # #### #### English-header #### ####
    # self.english_flag = (ord(struct.unpack_from("c", fp.read(1))[0]) != 0)
    # if self.english_flag:
    #     self.english_head = {}
    #     en_model_name, en_comment = struct.unpack_from("20s256s", fp.read(20 + 256))
    #     self.english_head["name"] = padding_erase(en_model_name.decode("cp932", "ignore"), 'f8')
    #     self.english_head["comment"] = padding_erase(en_comment.decode("cp932", "ignore"), 'f8')

    #     print(self.english_head["name"])
    #     print(self.english_head["comment"])

    #     # bone name
    #     self.bone["en_name"] = []
    #     for _ in range(self.bone_size):
    #         en_name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
    #         self.bone["en_name"].append(en_name)

    #     # skin name
    #     self.skin["en_name"] = []
    #     for _ in range(self.skin_size - 1):
    #         en_name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
    #         self.skin["en_name"].append(en_name)

    #     # bone disp name
    #     self.bone_disp["en_name"] = []
    #     for _ in range(self.bone_disp_size):
    #         en_name = padding_erase(struct.unpack_from("50s", fp.read(50))[0].decode("cp932", "ignore"), 'f8')
    #         self.bone_disp["en_name"].append(en_name)

    # # #### #### Toon-name #### ####
    # self.toon_name = {"name": []}
    # for i in range(10):
    #     name = struct.unpack_from("100s", fp.read(100))[0]
    #     self.toon_name["name"].append(name)

    # # #### #### Physics #### ####
    # self.physics_size = loop_size = struct.unpack_from("h", fp.read(4))[0]
    # self.physics_flag = (loop_size > 0)
    # if self.physics_flag:
    #     self.physics = {"body": {}, "joint": {}}
    #     body = self.physics["body"]
    #     body = {"name": [], "bone_id": [], "group_id": [], "group_mask": [], "type_id": [], "whd": [], "pos": [], "rot": [], "mass": [], \
    #         "pos_dim": [], "rot_dim": [], "recoil": [], "friction": [], "calc": []}

    #     # 剛体
    #     for i in range(loop_size):
    #         name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
    #         bone_id = struct.unpack_from("h", fp.read(2))[0]
    #         group_id = ord(struct.unpack_from("c", fp.read(1))[0])
    #         group_mask = hex(struct.unpack_from("h", fp.read(2))[0])
    #         type_id = ord(struct.unpack_from("c", fp.read(1))[0])
    #         whd = struct.unpack_from("3f", fp.read(12))
    #         pos = struct.unpack_from("3f", fp.read(12))
    #         rot = struct.unpack_from("3f", fp.read(12))
    #         mass = struct.unpack_from("f", fp.read(4))
    #         pos_dim = struct.unpack_from("f", fp.read(4))
    #         rot_dim = struct.unpack_from("f", fp.read(4))
    #         recoil = struct.unpack_from("f", fp.read(4))
    #         friction = struct.unpack_from("f", fp.read(4))
    #         calc = ord(struct.unpack_from("c", fp.read(1))[0])

    #         body["name"].append(name)
    #         body["bone_id"].append(bone_id)
    #         body["group_id"].append(group_id)
    #         body["group_mask"].append(group_mask)
    #         body["type_id"].append(type_id)
    #         body["whd"].append(whd)
    #         body["pos"].append(pos)
    #         body["rot"].append(rot)
    #         body["mass"].append(mass)
    #         body["pos_dim"].append(pos_dim)
    #         body["rot_dim"].append(rot_dim)
    #         body["recoil"].append(recoil)
    #         body["friction"].append(friction)
    #         body["calc"].append(calc)

    #     # ジョイント
    #     self.joint_size = loop_size = struct.unpack_from("h", fp.read(4))[0]
    #     joint = self.physics["joint"] = {"name": [], "rigidbody_a": [], "rigidbody_b": [],
    #                 "pos": [], "rot": [],
    #                 "constrain_pos": [],
    #                 "spring_pos": [], "spring_rot": []}
    #     for i in range(loop_size):
    #         name = padding_erase(struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore"), 'f8')
    #         rigidbody_a = hex(struct.unpack_from("i", fp.read(4))[0])
    #         rigidbody_b = hex(struct.unpack_from("i", fp.read(4))[0])

    #         pos = struct.unpack_from("3f", fp.read(12))
    #         rot = struct.unpack_from("3f", fp.read(12))

    #         constrain_pos_1 = struct.unpack_from("3f", fp.read(12))
    #         constrain_pos_2 = struct.unpack_from("3f", fp.read(12))
    #         constrain_pos_3 = struct.unpack_from("3f", fp.read(12))
    #         constrain_pos_4 = struct.unpack_from("3f", fp.read(12))

    #         spring_pos = struct.unpack_from("3f", fp.read(12))
    #         spring_rot = struct.unpack_from("3f", fp.read(12))

    #         joint["name"].append(name)
    #         joint["rigidbody_a"].append(rigidbody_a)
    #         joint["rigidbody_b"].append(rigidbody_b)

    #         joint["pos"].append(pos)
    #         joint["rot"].append(rot)

    #         joint["constrain_pos"].append([constrain_pos_1, constrain_pos_2, constrain_pos_3, constrain_pos_4])

    #         joint["spring_pos"].append(spring_pos)
    #         joint["spring_rot"].append(spring_rot)

    return True
