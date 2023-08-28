from __future__ import annotations
import numpy as np
from typing import Any
from . import mmdpy_bone


class mmdpyMotionFrame:
    def __init__(self, bone: mmdpy_bone.mmdpyBone, frame: int):
        self.bone: mmdpy_bone.mmdpyBone = bone
        self.frame: int = frame
        self.qs: None | np.ndarray = None
        self.pos: None | np.ndarray = None
        self.next: None | mmdpyMotionFrame = None

    def get_frame(self) -> int:
        return self.frame

    def get_position(self) -> None | np.ndarray:
        return self.pos

    def get_quaternion(self) -> None | np.ndarray:
        return self.qs

    def set_next_motion(self, motion: None | mmdpyMotionFrame) -> None:
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

    def update(self, frame: int) -> mmdpyMotionFrame | None:
        # self.bone.add_matrix(np.identity(4), overwrite=True)

        if self.next is None and self.qs is not None:
            matrix = self.quaternion2matrix(self.qs)
            self.bone.add_matrix(matrix)
            return self

        rate = self.get_rate(frame)
        if rate > 1.00:
            return self.next

        # 位置補間
        pos = self.interpolate(rate)
        self.bone.slide(pos)

        # クォータニオン線形補間
        qs = self.slerp_quaternion(rate)
        matrix = self.quaternion2matrix(qs)
        self.bone.add_matrix(matrix)

        # Frame をすすめるか
        if self.next and self.next.frame <= frame:
            return self.next
        return self

    def get_rate(self, frame: int) -> float:
        rate = 0.50
        if self.next:
            if self.next.frame == self.frame:
                rate = 0.00
            else:
                rate = (frame - self.frame) / (self.next.frame - self.frame)
        if rate < 0.00 or 1.00 < rate:
            return 1.00 + 1e-8
        return rate

    def interpolate(self, rate: float) -> np.ndarray:
        p0 = np.zeros(4)
        if self.pos:
            p0 = self.pos
        p1 = p0
        if self.next and self.next.pos:
            p1 = self.next.pos
        return rate * np.array(p1) + (1 - rate) * np.array(p0)

    # 線形球面補完
    def slerp_quaternion(self, rate: float) -> np.ndarray:

        q0 = np.zeros(4)
        if self.qs:
            q0 = self.qs
        q1 = q0
        if self.next and self.next.qs:
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
        self.motions: dict[str, list[None | mmdpyMotionFrame]] = {}
        self.bone_frame: dict[str, Any] = {}
        self.now_frame: dict[str, Any] = {}
        motion_frame: dict[str, Any] = {}
        for b in self.model.bones:
            self.motions[b.name] = []
            motion_frame[b.name] = []

        if motion is None:
            return

        for m in motion.motions:
            if m.bonename in motion_frame.keys():
                motion_frame[m.bonename].append(m)

        for k, v in motion_frame.items():
            for m in v:
                motion_temp = mmdpyMotionFrame(self.model.get_bone_by_name(m.bonename), m.frame)
                motion_temp.set_quaternion(m.quaternion)
                motion_temp.set_position(m.vector)
                self.motions[k].append(motion_temp)
            for m, nm in zip(self.motions[k], self.motions[k][1:] + [None]):
                if m is not None:
                    m.set_next_motion(nm)

        for b in model.bones:
            self.motions[b.name].append(None)

        for k, v in self.motions.items():
            self.now_frame[k] = v[0]

    # モーションの終了判定
    def finish(self) -> bool:
        for b in self.model.bones:
            now_frame = self.now_frame[b.name]
            if now_frame is not None:
                return False  # 再生中モーションあり
        return True  # モーションはすべて再生終了

    def update(self, frame: int) -> None:
        for b in self.model.bones:
            if b.name not in self.now_frame.keys():
                continue
            now_frame = self.now_frame[b.name]
            if now_frame is not None:
                self.now_frame[b.name] = now_frame.update(frame)

    # モーションを間に追加もしくは、すでにモーションがそのフレームに存在する場合は更新する
    def change_motion(self, bonename: str, frame: int,
                      position: np.ndarray,
                      quaternion: np.ndarray) -> mmdpyMotionFrame:

        motions: list[None | mmdpyMotionFrame] = self.motions[bonename]
        change_flag: bool = False  # 既存のフレームを更新する場合 True <= 変更要望フレームが既に存在する
        target_index: int = 0
        for i, motion_temp in enumerate(motions):
            target_index = i
            if motion_temp is not None:
                if frame == motion_temp.get_frame():
                    change_flag = True
                    break
                if frame >= motion_temp.get_frame():
                    break

        new_motion: mmdpyMotionFrame = mmdpyMotionFrame(self.model.get_bone_by_name(bonename), frame)
        new_motion.set_position(position)
        new_motion.set_quaternion(quaternion)

        if change_flag:
            self.motions[bonename][target_index] = new_motion
        else:
            after_motion: list[None | mmdpyMotionFrame] = self.motions[bonename][target_index:]
            if len(after_motion) == 0:
                after_motion = [None]
            self.motions[bonename] = \
                self.motions[bonename][:target_index] + [new_motion] + after_motion
            if after_motion[0] is None:
                self.now_frame[bonename] = new_motion

        return new_motion
