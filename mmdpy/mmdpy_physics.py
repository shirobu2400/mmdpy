import numpy as np
from typing import List
import pybullet as pbt
from . import mmdpy_type
from . import mmdpy_bone


class mmdpyPhysics:
    def __init__(self,
                 bone: List[mmdpy_bone.mmdpyBone],
                 body: List[mmdpy_type.mmdpyTypePhysicsBody],
                 joint: List[mmdpy_type.mmdpyTypePhysicsJoint]):
        self.bone = bone
        self.body = body
        self.joint = joint

        # 世界生成
        self.physics_client = pbt.connect(pbt.DIRECT)
        # self.physics_client = pbt.connect(pbt.GUI)
        pbt.setGravity(0, 0, -9.81)

        # リアルタイム
        pbt.setRealTimeSimulation(1)

        # オブジェクトの生成
        for r in self.body:
            # 剛体生成
            shape = None

            if r.type_id == 0:  # 球
                shape = pbt.createCollisionShape(pbt.GEOM_SPHERE, radius=r.sizes[0])
            if r.type_id == 1:  # 箱
                shape = pbt.createCollisionShape(pbt.GEOM_BOX,
                                                 halfExtents=[0.50 * r.sizes[0], 0.50 * r.sizes[1], 0.50 * r.sizes[2]])
            if r.type_id == 2:  # カプセル
                shape = pbt.createCollisionShape(pbt.GEOM_CAPSULE, radius=r.sizes[0], height=r.sizes[1])

            if shape is None:
                continue

            if r.calc == 0:  # 固定
                r.mass = 0
            b = pbt.createMultiBody(r.mass, shape, -1)
            pbt.changeDynamics(b, -1, spinningFriction=r.friction, rollingFriction=0.001, linearDamping=0.00)

            # body を登録
            r.body = b
            r.bone = bone[r.bone_id]

            # 姿勢初期化
            q = r.bone.get_quaternion()
            p = r.bone.get_position()
            p = self.convert_position(p)
            q = self.convert_quaternion(q)
            pbt.resetBasePositionAndOrientation(r.body, p, q)

        # joint
        for c in self.joint:
            self.body[c.rigidbody_a].bone.update_matrix()
            self.body[c.rigidbody_b].bone.update_matrix()
            rigidbody_a_pos = self.body[c.rigidbody_a].bone.get_position()
            rigidbody_b_pos = self.body[c.rigidbody_b].bone.get_position()
            rigidbody_a_pos = self.convert_position(rigidbody_a_pos)
            rigidbody_b_pos = self.convert_position(rigidbody_b_pos)

            rot = c.rot
            rot = self.convert_position(rot)

            cid = pbt.createConstraint(
                parentBodyUniqueId=self.body[c.rigidbody_a].body,
                parentLinkIndex=-1,
                childBodyUniqueId=self.body[c.rigidbody_b].body,
                childLinkIndex=-1,
                # jointType=pbt.JOINT_FIXED,
                jointType=pbt.JOINT_POINT2POINT,
                jointAxis=rot,
                parentFramePosition=rigidbody_a_pos,
                childFramePosition=rigidbody_b_pos,
                # parentFrameOrientation=rigidbody_a_pos,
                # childFrameOrientation=rigidbody_b_pos,
            )

            # save
            c.joint = cid

    def convert_position(self, p: np.ndarray) -> np.ndarray:
        return np.array([p[0], p[2], p[1]])

    def convert_quaternion(self, q: np.ndarray) -> np.ndarray:
        return np.array([q[0], q[2], q[1], q[3]])

    def run(self) -> None:
        pbt.stepSimulation()
        for r in self.body:
            if r.calc == 0:
                # 行列の物理演算への反映
                q = r.bone.get_quaternion()
                p = r.bone.get_position()
                p = self.convert_position(p)
                q = self.convert_quaternion(q)

                pbt.resetBasePositionAndOrientation(r.body, p, q)
            else:
                # 行列の表示ボーンへの反映
                p, q = pbt.getBasePositionAndOrientation(r.body)
                p = self.convert_position(p)
                q = self.convert_quaternion(q)

                r.bone.set_position(p)
                r.bone.set_quaternion(q)
                r.bone.update_local_matrix()
