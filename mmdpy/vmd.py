import struct
import os


class mmdpyVmd:
    def __init__(self, filename=None):
        self.motions = []
        self.frame_id = 0

        if not filename is None:
            if not self.load(filename):
                raise IOError

    def load(self, filename):
        def str_to_hex(s):
            return [hex(ord(i))[2:4] for i in s]
        def padding_erase(_string, ps):
            end_point = 0
            bins = str_to_hex(_string)
            length = len(_string)
            while bins[end_point] != ps and end_point < length - 1:
                end_point += 1
            return _string[:end_point]

        class empty:
            pass

        self.filename = filename
        self.path, self.ext = os.path.splitext(filename)
        self.directory = os.path.dirname(filename) + "/"

        try:
            fp = open(filename, "rb")
        except IOError:
            return False

        print("/**** **** **** **** Motion File Informations **** **** **** ****/")
        # #### #### header #### ####
        head = struct.unpack_from("30s", fp.read(30))[0]
        print(head.decode("cp932", "ignore"))
        if not b"Vocaloid Motion Data 0002" in head:
            return False

        modelname = struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore")
        modelname = padding_erase(modelname, 'f8')
        print(modelname)

        # #### #### data #### ####

        # Bone
        loop_size = struct.unpack_from("i", fp.read(4))[0]
        for _ in range(loop_size):
            motion = empty()

            motion.bonename   = struct.unpack_from("15s", fp.read(15))[0].decode("cp932", "ignore")
            motion.bonename   = padding_erase(motion.bonename, 'f8')
            motion.bonename   = padding_erase(motion.bonename, '00')

            motion.frame      = struct.unpack_from("i", fp.read(4))[0]
            motion.vector     = struct.unpack_from("3f", fp.read(12))
            motion.quaternion = struct.unpack_from("4f", fp.read(16))
            motion.interpolation = struct.unpack_from("16f", fp.read(64))

            self.motions.append(motion)
        self.motions = sorted(self.motions, key=lambda m: m.frame)

        # Skin
        # これから実装するかも

        return True
