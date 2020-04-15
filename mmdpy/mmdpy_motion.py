import numpy as np

class mmdpyMotionFrame:
    def __init__(self, bone, frame):
        self.bone = bone
        self.frame = frame
        self.qs = None
        self.pos = None
        self.next = None

    def setNextMotion(self, motion):
        self.next = motion

    def setQuaternion(self, qs):
        self.qs = qs

    def setPosition(self, pos, interpolation):
        self.pos = pos

    def quaternion2matrix(self, qt):
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

    def update(self, frame):
        self.bone.addMatrix(np.identity(4), overwrite=True)

        if self.next is None:
            matrix = self.quaternion2matrix(self.qs)
            self.bone.addMatrix(matrix)
            return self

        if self.next.frame == self.frame:
            rate = 0
        else:
            rate = (frame - self.frame) / (self.next.frame - self.frame)
        if rate < 0 or 1 < rate:
            return self.next

        pos = self.interpolate(rate)
        self.bone.slide(pos)

        qs = self.slerp_quaternion(rate)
        matrix = self.quaternion2matrix(qs)
        self.bone.addMatrix(matrix)

        # Frame をすすめるか
        if self.next.frame <= frame:
            return self.next
        return self

    def interpolate(self, rate):
        v = rate * np.array(self.next.pos) + (1 - rate) * np.array(self.pos)
        return v

    # 線形球面補完
    def slerp_quaternion(self, rate):
        q0 = self.qs
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
        s1 = np.sin(ph * (    rate)) / sph
        return q0 * s0 + q1 * s1 * s1_sign

class mmdpyMotion:
    def __init__(self, model, motion):
        self.model = model
        self.motions = {}
        self.bone_frame = {}
        self.now_frame = {}

        motion_frame = {}
        for b in model.bones:
            self.motions[b.name] = []
            motion_frame[b.name] = []

        for m in motion.motions:
            if m.bonename in motion_frame.keys():
                motion_frame[m.bonename].append(m)

        for k, v in motion_frame.items():
            for m in v:
                motion = mmdpyMotionFrame(model.getBoneByName(m.bonename), m.frame)
                motion.setQuaternion(m.quaternion)
                motion.setPosition(m.vector, None)
                self.motions[k].append(motion)
            for m, nm in zip(self.motions[k], self.motions[k][1:] + [None]):
                m.setNextMotion(nm)

        for b in model.bones:
            self.motions[b.name].append(None)

        for k, v in self.motions.items():
            self.now_frame[k] = v[0]

    def update(self, frame):
        for b in self.model.bones:
            now_frame = self.now_frame[b.name]
            if now_frame is not None:
                self.now_frame[b.name] = now_frame.update(frame)
