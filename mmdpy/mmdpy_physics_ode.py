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
            elif body.type_id == 1:  # 箱
                mass.setBox(density, body.sizes[0], body.sizes[1], body.sizes[2])
                ode_geom = ode.GeomBox(self.space, lengths=body.sizes)
            elif body.type_id == 2:  # カプセル
                mass.setCylinder(density, 2, body.sizes[0], body.sizes[1])
                ode_geom = ode.GeomCylinder(self.space, radius=body.sizes[0], length=body.sizes[1])
            else:
                mass.setSphere(density, body.sizes[0])
                ode_geom = ode.GeomSphere(self.space, radius=body.sizes[0])

            mass.mass = max(1, (1 if body.calc == 0 else body.mass / density))
            ode_body.setMass(mass)
            if ode_geom is not None:
                ode_geom.setBody(ode_body)

            # reset positions.
            ode_body.setPosition(body.pos)

            q: np.ndarray = scipy.spatial.transform.Rotation.from_rotvec(body.rot).as_matrix()
            ode_body.setRotation(q.reshape(9))

            # # debug
            # body.calc = 0

            self.ode_bodies.append(ode_body)
            self.ode_geoms.append(ode_geom)

        # joint
        # https://so-zou.jp/robot/tech/physics-engine/ode/joint/
        for i, joint in enumerate(self.joints):
            joint.cid = i

            body_a = self.ode_bodies[joint.rigidbody_a]
            body_b = self.ode_bodies[joint.rigidbody_b]

            ode_joint = ode.BallJoint(self.world)
            # ode_joint = ode.FixedJoint(self.world)
            # ode_joint = ode.HingeJoint(self.world)

            # ode_joint.attach(ode.environment, body_a)
            ode_joint.attach(body_a, body_b)
            # print(joint.pos, body_a.getPosition())
            # ode_joint.setAnchor(body_a.getPosition())
            # ode_joint.setAnchor(joint.pos)
            ode_joint.setAnchor(np.array(joint.pos) + np.array(body_a.getPosition()))

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
            # self.bodies[joint.rigidbody_b].calc = 1

        # 環境に張り付け
        origin_bodies = [(x, y) for (x, y) in enumerate(self.bodies) if y.calc == 0]
        for i, body in origin_bodies:
            ode_body = self.ode_bodies[i]
            ode_joint = ode.BallJoint(self.world)
            ode_joint.attach(ode.environment, ode_body)
            # ode_joint.setAnchor(body.pos)
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

    @staticmethod
    def scalp(vec: np.ndarray, scal: float) -> np.ndarray:
        vec[0] *= scal
        vec[1] *= scal
        vec[2] *= scal
        return vec

    @staticmethod
    def length(vec: np.ndarray) -> float:
        return np.sqrt(vec[0]**2 + vec[1]**2 + vec[2]**2)

    def run(self, n: int = 1) -> None:
        dt: float = (time.time() - self.prev_time) / n
        self.prev_time = time.time()

        origin_bodies = [(x, y) for (x, y) in enumerate(self.bodies) if y.calc == 0]
        update_bodies = [(x, y) for (x, y) in enumerate(self.bodies) if y.calc != 0]
        for i, body in origin_bodies:
            ode_body = self.ode_bodies[i]

            # 行列の物理演算への反映
            p = body.bone.get_position()
            ode_body.setPosition(p)

            q = body.bone.get_rotmatrix()
            ode_body.setRotation(q.reshape(9))

        for _ in range(n):

            # Detect collisions and create contact joints
            self.space.collide((self.world, self.contactgroup), self.near_callback)

            # run simulation
            self.world.step(dt)

            # Remove all contact joints
            self.contactgroup.empty()

        # pull object
        f = True
        for i, body in update_bodies:
            ode_body = self.ode_bodies[i]

            x2, y2, z2 = body.bone.get_position()

            x, y, z = ode_body.getPosition()
            rot = ode_body.getRotation()
            matrix = np.array([[rot[0], rot[3], rot[6], 0],
                               [rot[1], rot[4], rot[7], 0],
                               [rot[2], rot[5], rot[8], 0],
                               [x, y, z, 1.0]])
            body.bone.set_matrix(matrix)
            body.bone.local_matrix = np.matmul(body.bone.offset_matrix, body.bone.global_matrix)

            if f:
                print(body.name, (x2, y2, z2), (x, y, z))
                f = False
