import OpenGL
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import *
import numpy as np
from . import mmdpy_shader

class mmdpyMesh:

    def __init__(self, index, shader, vertex, face, material, bone):
        self.index = index
        self.shader = shader
        ver = []
        uv = []
        bone_id = []
        bone_weight = []
        for v in vertex:
            ver.append(v.ver)
            uv.append(v.uv)
            bone_id.append(v.bone_id)
            bone_weight.append(v.bone_weight)

        self.vertex = np.array(ver, dtype=(np.float32))
        self.uv = np.array(uv, dtype=(np.float32))
        self.bone_id = np.array(bone_id, dtype=(np.float32))
        self.bone_weight = np.array(bone_weight, dtype=(np.float32))
        self.face = np.array(face, dtype=(np.uint16))
        self.material = material
        self.bone = bone
        self.glsl_info = self.shader.setBuffers(self.vertex, self.uv, self.face)
        self.shader.setBone(self.glsl_info, self.bone_id, self.bone_weight)
        self.shader.setTexture(self.glsl_info, self.material.texture)
        self.shader.setMaterial(self.glsl_info, self.material)

    def draw(self):
        self.shader.setBoneMatrix(self.glsl_info, [x.local_matrix for x in self.bone])
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glFrontFace(GL_CCW)
        glCullFace(GL_BACK)
        glEnable(GL_TEXTURE_2D)
        glActiveTexture(GL_TEXTURE0)
        self.shader.draw(self.glsl_info)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)
