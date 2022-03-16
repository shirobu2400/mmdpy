from __future__ import annotations
import struct
import os
from typing import List, Tuple, Any
from dataclasses import dataclass, field
import numpy as np


@dataclass
class mmdpyVmdMotion:
    """"Motion dataclass"""
    bonename: str = field(default="")
    frame: int = field(default=0)
    vector: Tuple[Any, ...] = field(default=(0, 0, 0))
    quaternion: Tuple[Any, ...] = field(default=(0, 0, 0, 0))
    interpolation: Tuple[Any, ...] = field(default=(0, 0, 0, 0))


class mmdpyVmd:
    def __init__(self, filename: str = ""):
        """"MMDPY Motion Class"""
        self.motions: List[mmdpyVmdMotion] = []
        self.frame_id = 0

        if filename != "":
            if not self.load(filename):
                raise IOError

    @staticmethod
    def str_to_hex(s: str) -> List[str]:
        return [hex(ord(i))[2:4] for i in s]

    def padding_erase(self, _string: str, ps: str) -> str:
        end_point = 0
        bins = self.str_to_hex(_string)
        length = len(_string)
        while end_point < length - 1 and bins[end_point] != ps:
            end_point += 1
        return _string[:end_point]

    def load(self, filename: str) -> bool:

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
        if b"Vocaloid Motion Data 0002" not in head:
            return False

        modelname = struct.unpack_from("20s", fp.read(20))[0].decode("cp932", "ignore")
        modelname = self.padding_erase(modelname, 'f8')
        print(modelname)

        # #### #### data #### ####

        # Bone
        loop_size = struct.unpack_from("L", fp.read(4))[0]
        for _ in range(loop_size):
            motion = mmdpyVmdMotion()

            motion.bonename = struct.unpack_from("15s", fp.read(15))[0].decode("cp932", "ignore")
            motion.bonename = self.padding_erase(motion.bonename, 'f8')
            motion.bonename = self.padding_erase(motion.bonename, '00')

            motion.frame = struct.unpack_from("L", fp.read(4))[0]
            motion.vector = struct.unpack_from("3f", fp.read(12))
            motion.quaternion = struct.unpack_from("4f", fp.read(16))
            motion.interpolation = struct.unpack_from("16f", fp.read(64))

            self.motions.append(motion)
        self.motions = sorted(self.motions, key=lambda m: m.frame)

        # Skin
        # これから実装するかも
        fp.close()

        return True

    # 共有のMotionデータからVMDを生成
    def convert_vmd(self, motions: Any) -> mmdpyVmd:
        vmd: mmdpyVmd = mmdpyVmd()
        for bonename, motion_list in motions.motions.items():
            for motion in motion_list:
                if not motion:
                    continue
                vmd_motion: mmdpyVmdMotion = mmdpyVmdMotion()

                vmd_motion.bonename = bonename
                vmd_motion.frame = motion.get_frame()
                vmd_motion.vector = motion.get_position()
                q = motion.get_quaternion()
                vmd_motion.quaternion = (-q[0], -q[1], -q[2], q[3])
                vmd_motion.interpolation = np.zeros(4 * 4, dtype=np.float16).tolist()

                vmd.motions.append(vmd_motion)

        return vmd

    def save(self, filename: str, motions: mmdpyVmd) -> bool:

        self.filename = filename
        self.path, self.ext = os.path.splitext(filename)
        self.directory = os.path.dirname(filename) + "/"

        try:
            fp = open(filename, "wb")
        except IOError:
            return False

        # header
        fp.write(b'Vocaloid Motion Data 0002\x00\x00\x00\x00\x00')
        fp.write(b'Dummy Model Name    ')

        fp.write(struct.pack('<L', len(motions.motions)))
        for motion in motions.motions:

            # ボーン名
            bonename = motion.bonename.encode("cp932", "ignore")
            fp.write(bonename)
            fp.write(bytearray([0 for _ in range(len(bonename), 15)]))

            # フレーム番号
            fp.write(struct.pack("<L", motion.frame))

            # 座標
            fp.write(struct.pack("<f", motion.vector[0]))
            fp.write(struct.pack("<f", motion.vector[1]))
            fp.write(struct.pack("<f", motion.vector[2]))

            # クォータニオン
            fp.write(struct.pack("<f", motion.quaternion[0]))
            fp.write(struct.pack("<f", motion.quaternion[1]))
            fp.write(struct.pack("<f", motion.quaternion[2]))
            fp.write(struct.pack("<f", motion.quaternion[3]))

            # 補完パラメータ保存
            fp.write(bytearray([0 for _ in range(0, 64)]))

        # これから実装するかも
        # スキン
        fp.write(struct.pack('<L', 0))

        # カメラキーフレーム数
        fp.write(struct.pack('<L', 0))

        # 照明キーフレーム数
        fp.write(struct.pack('<L', 0))

        # セルフ影キーフレーム数
        fp.write(struct.pack('<L', 0))

        # モデル表示・IK on/offキーフレーム数
        fp.write(struct.pack('<L', 0))

        fp.close()

        return True
