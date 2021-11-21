from __future__ import annotations
import numpy as np
from typing import Union, Dict, Any
from . import mmdpy_bone


class mmdpyMotionFrame:
    def __init__(self, bone: mmdpy_bone.mmdpyBone, frame: int):
        self.bone: mmdpy_bone.mmdpyBone = bone
        self.frame: int = frame
        self.qs: Union[None, np.ndarray] = None
        self.pos: Union[None, np.ndarray] = None
        self.next: Union[None, mmdpyMotionFrame] = None

    def set_next_motion(self, motion: Union[None, mmdpyMotionFrame]) -> None:
        self.next = motion

    def set_quaternion(self, qs: np.ndarray) -> None:
        self.qs = qs

    def set_position(self, pos: np.ndarray) -> None:
        self.pos = pos

    def quaternion2matrix(self, qt: np.ndarray) -> np.ndarray:
        matrix = np.identity(4)

        qx = qt[0]
        qy = qt[1]
        qz = qt[2]
        qw = qt[3]

        sx = qx * qx
        sy = qy * qy
        sz = qz * qz
        cx = qy * qz
        cy = qx * qz
        cz = qx * qy
        wx = qw * qx
        wy = qw * qy
        wz = qw * qz

        matrix[0, 0] = 1.00 - 2.00 * (sy + sz)
        matrix[0, 1] = 2.00 * (cz + wz)
        matrix[0, 2] = 2.00 * (cy - wy)

        matrix[1, 0] = 2.00 * (cz - wz)
        matrix[1, 1] = 1.00 - 2.00 * (sx + sz)
        matrix[1, 2] = 2.00 * (cx + wx)

        matrix[2, 0] = 2.00 * (cy + wy)
        matrix[2, 1] = 2.00 * (cx - wx)
        matrix[2, 2] = 1.00 - 2.00 * (sx + sy)

        return matrix

    def update(self, frame: int) -> Union[mmdpyMotionFrame, None]:
        self.bone.add_matrix(np.identity(4), overwrite=True)

        if self.next is None and self.qs is not None:
            matrix = self.quaternion2matrix(self.qs)
            self.bone.add_matrix(matrix)
            return self

        rate = 0.50
        if self.next:
            if self.next.frame == self.frame:
                rate = 0.00
            else:
                rate = (frame - self.frame) / (self.next.frame - self.frame)
        if rate < 0.00 or 1.00 < rate:
            return self.next

        pos = self.interpolate(rate)
        self.bone.slide(pos)

        qs = self.slerp_quaternion(rate)
        matrix = self.quaternion2matrix(qs)
        self.bone.add_matrix(matrix)

        # Frame をすすめるか
        if self.next and self.next.frame <= frame:
            return self.next
        return self

    def interpolate(self, rate: float) -> np.ndarray:
        v = np.zeros([3])
        if self.next:
            v = rate * np.array(self.next.pos) + (1 - rate) * np.array(self.pos)
        return v

    # 線形球面補完
    def slerp_quaternion(self, rate: float) -> np.ndarray:
        q0 = self.qs
        q1 = q0
        if self.next:
            q1 = self.next.qs

        q0 = np.array(q0)
        q1 = np.array(q1)

        qr = np.dot(q0, q1)
        ss = 1.00 - (qr * qr)
        if ss < 0.00:
            return q0
        if 1.00 < qr:
            return q0
        s1_sign = +1
        if qr < 0.00:
            qr = np.dot(-q0, q1)
            s1_sign = -1
        ph = np.arccos(qr)
        sph = np.sin(ph)
        if sph == 0.00:
            return q0
        s0 = np.sin(ph * (1 - rate)) / sph
        s1 = np.sin(ph * rate) / sph
        return q0 * s0 + q1 * s1 * s1_sign


class mmdpyMotion:
    def __init__(self, model: Any, motion: Any):
        self.model = model
        self.motions: Dict[str, Any] = {}
        self.bone_frame: Dict[str, Any] = {}
        self.now_frame: Dict[str, Any] = {}
        motion_frame: Dict[str, Any] = {}
        for b in model.bones:
            self.motions[b.name] = []
            motion_frame[b.name] = []

        for m in motion.motions:
            if m.bonename in motion_frame.keys():
                motion_frame[m.bonename].append(m)

        for k, v in motion_frame.items():
            for m in v:
                motion = mmdpyMotionFrame(model.get_bone_by_name(m.bonename), m.frame)
                motion.set_quaternion(m.quaternion)
                motion.set_position(m.vector)
                self.motions[k].append(motion)
            for m, nm in zip(self.motions[k], self.motions[k][1:] + [None]):
                m.set_next_motion(nm)

        for b in model.bones:
            self.motions[b.name].append(None)

        for k, v in self.motions.items():
            self.now_frame[k] = v[0]

    def update(self, frame: int) -> None:
        for b in self.model.bones:
            now_frame = self.now_frame[b.name]
            if now_frame is not None:
                self.now_frame[b.name] = now_frame.update(frame)
