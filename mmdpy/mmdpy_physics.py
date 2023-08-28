import numpy as np
import scipy.spatial.transform.rotation as scipyrot
import pybullet
from . import mmdpy_type
from . import mmdpy_bone


class mmdpyPhysics:
    def __init__(self,
                 bones: list[mmdpy_bone.mmdpyBone],
                 bodies: list[mmdpy_type.mmdpyTypePhysicsBody],
                 joints: list[mmdpy_type.mmdpyTypePhysicsJoint]):
        self.bones: list[mmdpy_bone.mmdpyBone] = bones
        self.bodies: list[mmdpy_type.mmdpyTypePhysicsBody] = bodies
        self.joints: list[mmdpy_type.mmdpyTypePhysicsJoint] = joints

        # debug mode.
        debug_print: bool = True

        self.b2gl_p_scale: float = 0.50
        self.gl2b_p_scale: float = 1.00 / self.b2gl_p_scale

        # 世界生成
        if debug_print:
            # debug mode.
            self.physics_engine = pybullet.connect(pybullet.GUI, options="--opengl2")
            # pybullet.resetDebugVisualizerCamera(cameraDistance=35, cameraYaw=0, cameraPitch=0, cameraTargetPosition=[0, 0, 20])
            pybullet.resetDebugVisualizerCamera(cameraDistance=15, cameraYaw=180, cameraPitch=89, cameraTargetPosition=[0, 20, -10])
            # pybullet.setGravity(0, 0, 9.81, physicsClientId=self.physics_engine)
        else:
            self.physics_engine = pybullet.connect(pybullet.DIRECT)
        pybullet.setGravity(0, -9.81, 0, physicsClientId=self.physics_engine)

        # 剛体
        for body in self.bodies:
            body.cid = None
            body.bid = None
            body.bone = None

        for body in self.bodies:
            body.bone = self.bones[body.bone_id]
            cid = None

            rot: scipyrot.Rotation = scipyrot.Rotation.from_rotvec(body.rot)
            if body.type_id == 0:  # 球
                cid = pybullet.createCollisionShape(pybullet.GEOM_SPHERE,
                                                    radius=body.sizes[0],
                                                    physicsClientId=self.physics_engine)
            elif body.type_id == 1:  # 箱
                cid = pybullet.createCollisionShape(pybullet.GEOM_BOX,
                                                    halfExtents=body.sizes * self.b2gl_p_scale,
                                                    physicsClientId=self.physics_engine)
            elif body.type_id == 2:  # カプセル
                cid = pybullet.createCollisionShape(pybullet.GEOM_CAPSULE,
                                                    radius=body.sizes[0], height=body.sizes[1],
                                                    # collisionFrameOrientation=quat,
                                                    physicsClientId=self.physics_engine)
            else:
                cid = pybullet.createCollisionShape(pybullet.GEOM_SPHERE,
                                                    radius=body.sizes[0],
                                                    physicsClientId=self.physics_engine)

            # モデルから反映するボーンは重さ０とする
            if body.calc == 0:
                body.mass = 0
            bid = pybullet.createMultiBody(body.mass,
                                           cid,
                                           -1,
                                           body.pos,
                                           rot.as_quat(),
                                           physicsClientId=self.physics_engine)
            pybullet.changeDynamics(
                bid,
                -1,
                physicsClientId=self.physics_engine
            )

            body.cid = cid
            body.bid = bid

        self.origin_bodies: list[mmdpy_type.mmdpyTypePhysicsBody] \
            = [body for body in self.bodies if body.bone is not None and body.calc == 0]
        self.update_bodies: list[mmdpy_type.mmdpyTypePhysicsBody] \
            = [body for body in self.bodies if body.calc != 0 and body.bone is not None and body.bid is not None]
        self._set_origin_bones(self.origin_bodies)
        self._set_origin_bones(self.update_bodies)

        max_force: float = 1e+5

        # joint
        for joint in self.joints:
            body_a = self.bodies[joint.rigidbody_a]
            body_b = self.bodies[joint.rigidbody_b]
            if body_a.bid is None or body_b.bid is None:
                continue

            rot_a = scipyrot.Rotation.from_rotvec(body_a.rot)
            rot_b = scipyrot.Rotation.from_rotvec(body_b.rot)
            # rot_a = rot_a * self.gl2b_rot
            # rot_b = rot_b * self.gl2b_rot

            # cpos = np.subtract(body_a.pos, body_b.pos)
            parent_pos = np.matmul(body_a.bone.offset_matrix, np.concatenate([joint.pos, [1]], axis=0))
            child_pos = np.matmul(body_b.bone.offset_matrix, np.concatenate([joint.pos, [1]], axis=0))

            cid = pybullet.createConstraint(
                parentBodyUniqueId=body_a.bid,
                parentLinkIndex=-1,
                childBodyUniqueId=body_b.bid,
                childLinkIndex=-1,
                # jointType=pybullet.JOINT_POINT2POINT,
                jointType=pybullet.JOINT_FIXED,
                jointAxis=joint.rot,
                parentFramePosition=parent_pos,
                childFramePosition=child_pos,
                # parentFramePosition=[0, 0, 0],
                # childFramePosition=cpos,
                parentFrameOrientation=rot_a,
                childFrameOrientation=rot_b
            )
            cid = pybullet.changeConstraint(cid, maxForce=max_force, erp=0)

            joint.cid = cid

        self._update_bones(self.update_bodies)

        # リアルタイム
        pybullet.setRealTimeSimulation(1)

        self._set_origin_bones(self.origin_bodies)

    def _set_origin_bones(self, bones: list[mmdpy_type.mmdpyTypePhysicsBody]) -> None:
        for body in bones:
            # # 行列の物理演算への反映
            # # p: np.ndarray = body.bone.get_position_delta() + body.pos
            # # p: np.ndarray = self.gl2b_p_scale * np.array(body.bone.get_position())
            # p: np.ndarray = body.bone.get_position() + body.pos - body.bone.top_matrix[3, 0: 3]

            # q: scipyrot.Rotation \
            #     = scipyrot.Rotation.from_matrix(body.bone.delta_matrix[0:3, 0:3])
            # rot: scipyrot.Rotation = scipyrot.Rotation.from_rotvec(body.rot)
            # rot = rot * self.gl2b_rot
            # q = q * rot

            # pybullet.resetBasePositionAndOrientation(body.bid,
            #                                          np.array(p), q.as_quat(),
            #                                          physicsClientId=self.physics_engine)

            p = body.bone.get_position()
            q = body.bone.get_quaternion()
            pybullet.resetBasePositionAndOrientation(body.bid,
                                                     p, q,
                                                     physicsClientId=self.physics_engine)

    def _update_bones(self, bones: list[mmdpy_type.mmdpyTypePhysicsBody]) -> None:
        for body in bones:
            # 行列の表示ボーンへの反映
            p, q = pybullet.getBasePositionAndOrientation(body.bid, physicsClientId=self.physics_engine)
            body.bone.set_position(p)
            body.bone.set_quaternion(q)
            body.bone.local_matrix = np.matmul(body.bone.offset_matrix, body.bone.global_matrix)

    def run(self) -> None:
        self._set_origin_bones(self.origin_bodies)

        # # run simulation
        # pybullet.stepSimulation(self.physics_engine)

        self._update_bones(self.update_bodies)

    # def createURDF(
    #     self,
    #     bodies: List[mmdpy_type.mmdpyTypePhysicsBody],
    #     joints: List[mmdpy_type.mmdpyTypePhysicsJoint]
    # ) -> str:
    #     joints = joints[:16]

    #     joint_b_body_name: List[str] = [bodies[x.rigidbody_b].name for x in joints]

    #     urdf_str: str = "<?xml version=\"1.0\"?>\n"
    #     urdf_str = urdf_str + "<robot name=\"mmdpi_robot\">\n"
    #     # urdf_str = urdf_str + "<link name=\"base_link\" />\n"
    #     urdf_str = urdf_str + """<link name=\"base_link\"><inertial><mass value="0" /><inertia ixx="1" ixy="1" ixz="1" iyy="1" iyz="1" izz="1" /></inertial></link>\n"""

    #     for body in bodies:
    #         geometry_tag: str = ""
    #         if body.type_id == 0:  # 球
    #             geometry_tag = "<sphere radius=\"{}\" />".format(body.sizes[0])
    #         if body.type_id == 1:  # 箱
    #             geometry_tag = "<box size=\"{0} {1} {2}\" />".format(body.sizes[0], body.sizes[1], body.sizes[2])
    #         if body.type_id == 2:  # カプセル
    #             geometry_tag = "<cylinder radius=\"{0}\" length=\"{1}\" />".format(body.sizes[0], body.sizes[1])

    #         position_tag: str = "<origin xyz=\"{pos}\" rpy=\"{rot}\" />".format(
    #                 pos=" ".join([str(c) for c in body.pos]),
    #                 rot=" ".join([str(c) for c in [body.rot[0], body.rot[2], body.rot[1]]]),
    #             )

    #         mass_tag: str = "<mass value=\"{}\" />".format(1 if body.calc == 0 else body.mass)
    #         inertial_tag: str = "<inertia ixx=\"1\" ixy=\"1\" ixz=\"1\" iyy=\"1\" iyz=\"1\" izz=\"1\" />"

    #         urdf_str = urdf_str + """<link name="{}">""".format(body.name.replace("\0", ""))
    #         urdf_str = urdf_str \
    #             + "<inertial>{mass_tag}{inertial_tag}</inertial>{position_tag}<collision><geometry>{geometry_tag}</geometry></collision>".format(
    #                 geometry_tag=geometry_tag,
    #                 mass_tag=mass_tag,
    #                 inertial_tag=inertial_tag,
    #                 position_tag=position_tag,
    #             )
    #         urdf_str = urdf_str + "</link>\n"
    #         if body.name not in joint_b_body_name:
    #             urdf_str = urdf_str + \
    #                 "<joint name=\"base_joint_{name}\" type=\"fixed\"><parent link=\"base_link\"/><child link=\"{name}\" />{position_tag}</joint>\n".format(
    #                     name=body.name.replace("\0", ""),
    #                     position_tag=position_tag,
    #                 )

    #     joint_a_body_name: List[str] = []
    #     for joint in joints:
    #         if bodies[joint.rigidbody_b].name in joint_a_body_name:
    #             continue

    #         body_a_pos: np.ndarray = bodies[joint.rigidbody_a].pos
    #         body_b_pos: np.ndarray = bodies[joint.rigidbody_b].pos
    #         pos: np.ndarray = np.subtract(body_b_pos, body_a_pos)

    #         urdf_str = urdf_str + """<joint name="{name}" type="{jtype}"><parent link="{body_a}"/><child link="{body_b}"/>""".format(
    #             name=joint.name.replace("\0", ""),
    #             jtype="fixed",
    #             body_a=bodies[joint.rigidbody_a].name.replace("\0", ""),
    #             body_b=bodies[joint.rigidbody_b].name.replace("\0", ""),
    #         )
    #         urdf_str = urdf_str + "{limit}{axis}{origin}".format(
    #             limit="<limit lower=\"-1.5\" upper=\"1.5\" effort=\"0\" velocity=\"0\" />",
    #             axis="<axis xyz=\"{}\" />".format(" ".join([str(c) for c in joint.rot])),
    #             origin="""<origin xyz="{pos}" rpy="{rot}" />""".format(
    #                 pos=" ".join([str(c) for c in pos]),
    #                 rot=" ".join([str(c) for c in [0, 0, 0]])
    #             ),
    #         )
    #         urdf_str = urdf_str + "</joint>\n"
    #         joint_a_body_name.append(bodies[joint.rigidbody_b].name)

    #     urdf_str = urdf_str + "</robot>\n"
    #     return urdf_str
