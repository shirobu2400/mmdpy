import numpy as np
import time
from typing import List, Any
from . import mmdpy_type
from . import mmdpy_bone
import scipy.spatial.transform
import ode
# http://pyode.sourceforge.net/
# http://pyode.sourceforge.net/tutorials/tutorial1.html


class mmdpyPhysics:
    def __init__(self,
                 bones: List[mmdpy_bone.mmdpyBone],
                 bodies: List[mmdpy_type.mmdpyTypePhysicsBody],
                 joints: List[mmdpy_type.mmdpyTypePhysicsJoint]):
        self.bones: List[mmdpy_bone.mmdpyBone] = bones
        self.bodies: List[mmdpy_type.mmdpyTypePhysicsBody] = bodies
        self.joints: List[mmdpy_type.mmdpyTypePhysicsJoint] = joints

        self.ode_bodies: List[Any] = []
        self.ode_joints: List[Any] = []
        self.ode_geoms: List[Any] = []

        # 世界生成
        self.world = ode.World()
        self.world.setGravity([0, -9.81, 0])
        self.world.setERP(0.80)
        self.world.setCFM(1e-5)

        # Create a space object
        self.space = ode.Space()

        # A joint group for the contact joints that are generated whenever
        # two bodies collide
        self.contactgroup = ode.JointGroup()

        # 剛体
        for i, body in enumerate(self.bodies):
            body.cid = i
            body.bone = self.bones[body.bone_id]

            ode_body = ode.Body(self.world)
            mass = ode.Mass()
            density: float = 120.0
            ode_geom = None
            if body.type_id == 0:  # 球
                mass.setSphere(density, body.sizes[0])
                ode_geom = ode.GeomSphere(self.space, radius=body.sizes[0])
            if body.type_id == 1:  # 箱
                mass.setBox(density, body.sizes[0], body.sizes[1], body.sizes[2])
                ode_geom = ode.GeomBox(self.space, lengths=body.sizes)
            if body.type_id == 2:  # カプセル
                mass.setCylinder(density, 2, body.sizes[0], body.sizes[1])
                ode_geom = ode.GeomCylinder(self.space, radius=body.sizes[0], length=body.sizes[1])

            mass.mass = (1 if body.calc == 0 else body.mass / density)
            ode_body.setMass(mass)
            if ode_geom is not None:
                ode_geom.setBody(ode_body)

            ode_body.setPosition(body.pos)

            quat: np.ndarray = scipy.spatial.transform.Rotation.from_rotvec(body.rot).as_matrix().reshape(9)
            ode_body.setRotation(quat)

            # debug
            body.calc = 0

            self.ode_bodies.append(ode_body)
            self.ode_geoms.append(ode_geom)

        # joint
        # https://so-zou.jp/robot/tech/physics-engine/ode/joint/
        for i, joint in enumerate(self.joints[:1]):
            joint.cid = i

            body_a = self.ode_bodies[joint.rigidbody_a]
            body_b = self.ode_bodies[joint.rigidbody_b]

            ode_joint = ode.BallJoint(self.world)
            # ode_joint = ode.FixedJoint(self.world)
            # ode_joint = ode.HingeJoint(self.world)

            # ode_joint.attach(ode.environment, body_b)
            ode_joint.attach(body_a, body_b)
            ode_joint.setAnchor(joint.pos)

            # ode_joint = ode.UniversalJoint(self.world)
            # ode_joint.attach(body_a, body_b)
            # ode_joint.setAnchor(joint.pos)
            # ode_joint.setAxis1(joint.rot)
            # ode_joint.setParam(ode.ParamLoStop, joint.)

            self.ode_joints.append(ode_joint)

            # # 接続確認
            # print(
            #     self.bodies[joint.rigidbody_a].name,
            #     self.bodies[joint.rigidbody_b].name,
            #     ode.areConnected(body_a, body_b)
            # )
            # print(joint.pos, body_b.getPosition(), self.bodies[joint.rigidbody_b].pos)

            # debug
            self.bodies[joint.rigidbody_b].calc = 1

        for i, body in enumerate(self.bodies):
            ode_body = self.ode_bodies[i]
            if body.calc == 0:
                ode_joint = ode.BallJoint(self.world)
                ode_joint.attach(ode.environment, ode_body)
                ode_joint.setAnchor(body.pos)
                self.ode_joints.append(ode_joint)

        # 時刻保存
        self.prev_time: float = time.time()

    # Collision callback
    @staticmethod
    def near_callback(args, geom1, geom2):
        """Callback function for the collide() method.

        This function checks if the given geoms do collide and
        creates contact joints if they do.
        """

        # Check if the objects do collide
        contacts = ode.collide(geom1, geom2)

        # Create contact joints
        world, contactgroup = args
        for c in contacts:
            c.setBounce(0.20)
            c.setMu(5000)
            j = ode.ContactJoint(world, contactgroup, c)
            j.attach(geom1.getBody(), geom2.getBody())

    def run(self, n: int = 2) -> None:
        dt: float = (time.time() - self.prev_time) / n
        for _ in range(n):
            # # Detect collisions and create contact joints
            # self.space.collide((self.world, self.contactgroup), self.near_callback)

            for i, body in enumerate(self.bodies):
                if body.calc == 0:
                    ode_body = self.ode_bodies[i]

                    # 行列の物理演算への反映
                    p = body.bone.get_position_delta() + body.pos
                    ode_body.setPosition(p)

                    rotm = scipy.spatial.transform.Rotation.from_rotvec(body.rot).as_matrix()
                    q = np.matmul(body.bone.get_rotmatrix_delta(), rotm)
                    ode_body.setRotation(q.reshape(9))

            # run simulation
            self.world.step(dt)

            # Remove all contact joints
            self.contactgroup.empty()

        for i, body in enumerate(self.bodies):
            if body.calc != 0:
                ode_body = self.ode_bodies[i]

                p = ode_body.getPosition() - body.pos + body.bone.get_position()
                body.bone.set_position(p)

                rotm = scipy.spatial.transform.Rotation.from_rotvec(body.rot).as_matrix()
                q = ode_body.getRotation()
                q = np.array(q).reshape(3, 3)
                q = np.matmul(q, np.linalg.inv(rotm))
                q = np.matmul(q, body.bone.get_rotmatrix())
                body.bone.set_rotmatrix(q)

                body.bone.local_matrix = np.matmul(body.bone.offset_matrix, body.bone.global_matrix)

        self.prev_time = time.time()
