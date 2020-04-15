from . import mmdpy_root
import OpenGL
OpenGL.ERROR_ON_COPY = True
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GL.shaders import *
import numpy as np
MMDPY_MATERIAL_USING_BONE_NUM = mmdpy_root.MMDPY_MATERIAL_USING_BONE_NUM

class mmdpyShader:
    def __init__(self):
        self.program = None
        if not self.compile():
            raise IOError

    def draw(self, glsl_info):
        self.shaderOn()
        glUniform1f(self.glsl_id_is_texture, 0.0)
        if glsl_info.texture is not None:
            glUniform1f(self.glsl_id_is_texture, 1.0)
            glsl_info.texture.draw()
        glUniform4f(self.glsl_id_color, glsl_info.color[0], glsl_info.color[1], glsl_info.color[2], glsl_info.color[3])
        glUniform1f(self.glsl_id_alpha, glsl_info.alpha)
        glUniformMatrix4fv(self.glsl_id_bone_matrix, int(glsl_info.matrices.shape[0]), GL_FALSE, glsl_info.matrices)
        glBindVertexArray(glsl_info.glsl_vao)
        glDrawElements(GL_TRIANGLES, glsl_info.face_size, GL_UNSIGNED_SHORT, None)
        glBindVertexArray(0)
        self.shaderOff()

    def setBuffers(self, vertex, uv, face):
        class empty:
            pass

        glsl_info = empty
        face_size = len(face)
        face = np.array(face, dtype=(np.uint16))
        glsl_vbo_vertex = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, glsl_vbo_vertex)
        glBufferData(GL_ARRAY_BUFFER, vertex.nbytes, vertex, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glsl_vbo_uv = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, glsl_vbo_uv)
        glBufferData(GL_ARRAY_BUFFER, uv.nbytes, uv, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glsl_vao = glGenVertexArrays(1)
        glBindVertexArray(glsl_vao)
        glEnableVertexAttribArray(self.glsl_id_vertex)
        glEnableVertexAttribArray(self.glsl_id_uv)
        glBindBuffer(GL_ARRAY_BUFFER, glsl_vbo_vertex)
        glVertexAttribPointer(self.glsl_id_vertex, 3, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, glsl_vbo_uv)
        glVertexAttribPointer(self.glsl_id_uv, 2, GL_FLOAT, GL_FALSE, 0, None)
        glsl_vbo_face = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, glsl_vbo_face)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, face.nbytes, face, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glsl_info.glsl_vao = glsl_vao
        glsl_info.face_size = face_size
        return glsl_info

    def setBone(self, glsl_info, indexes, weights):
        glsl_vbo_bone_indexes = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, glsl_vbo_bone_indexes)
        glBufferData(GL_ARRAY_BUFFER, indexes.nbytes, indexes, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glsl_vbo_bone_weigths = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, glsl_vbo_bone_weigths)
        glBufferData(GL_ARRAY_BUFFER, weights.nbytes, weights, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(glsl_info.glsl_vao)
        glEnableVertexAttribArray(self.glsl_id_bone_indexes)
        glEnableVertexAttribArray(self.glsl_id_bone_weights)
        glBindBuffer(GL_ARRAY_BUFFER, glsl_vbo_bone_indexes)
        glVertexAttribPointer(self.glsl_id_bone_indexes, 4, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, glsl_vbo_bone_weigths)
        glVertexAttribPointer(self.glsl_id_bone_weights, 4, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glsl_info.index = indexes
        glsl_info.weight = weights

    def setTexture(self, glsl_info, texture):
        glsl_info.texture = texture

    def setMaterial(self, glsl_info, material):
        glsl_info.material = material
        glsl_info.alpha = material.alpha
        color = np.array((list(material.diffuse) + [1.0]), dtype=(np.float32))
        glsl_info.color = color
        glsl_info.alpha = glsl_info.alpha

    def setBoneMatrix(self, glsl_info, matrix):
        matrices = []
        for _ in range(MMDPY_MATERIAL_USING_BONE_NUM):
            matrices.append(matrix)

        glsl_info.matrices = np.array(matrices, dtype=(np.float32))

    def setProjectionMatrix(self, matrix=None, left=-0.5, right=0.5, top=-0.5, bottom=0.5, near=1.0, far=160.0):
        if matrix is None:
            matrix = self.perspectiveMatrix(left, right, top, bottom, near, far)
        glUniformMatrix4fv(self.glsl_id_projection_matrix, matrix)

    def perspectiveMatrix(self, left, right, top, bottom, near, far):
        dx = right - left
        dy = bottom - top
        dz = far - near
        matrix = np.array([16])
        matrix[0] = 2.0 * near / dx
        matrix[5] = 2.0 * near / dy
        matrix[8] = (right + left) / dx
        matrix[9] = (top + bottom) / dy
        matrix[10] = -(far + near) / dz
        matrix[11] = -1.0
        matrix[14] = -2.0 * far * near / dz
        matrix[1] = matrix[2] = matrix[3] = matrix[4] = matrix[6] = matrix[7] = matrix[12] = matrix[13] = matrix[15] = 0.0
        return matrix

    def shaderOn(self):
        if self.program is not None:
            glUseProgram(self.program)
        else:
            return False
        return True

    def shaderOff(self):
        glUseProgram(0)

    def compile(self):
        vertex_shader_src = """
            #version 110
            // uniform     mat4    ProjectionMatrix;
            mat4                ProjectionMatrix = gl_ModelViewProjectionMatrix;
            attribute   vec3    Vertex;
            attribute   vec2    InputUV;
            varying     vec2    ShareUV;
            uniform     vec4    InputColor;
            varying     vec4    ShareColor;
            attribute   vec4    BoneWeights;
            attribute   vec4    BoneIndices;
            uniform     mat4    BoneMatrix[%d];
            void main( void )
            {
                mat4            skinTransform;

                skinTransform  = BoneWeights[ 0 ] * BoneMatrix[ int( BoneIndices[ 0 ] ) ];
                skinTransform += BoneWeights[ 1 ] * BoneMatrix[ int( BoneIndices[ 1 ] ) ];
                skinTransform += BoneWeights[ 2 ] * BoneMatrix[ int( BoneIndices[ 2 ] ) ];
                skinTransform += BoneWeights[ 3 ] * BoneMatrix[ int( BoneIndices[ 3 ] ) ];

                gl_Position = ProjectionMatrix * skinTransform * vec4( Vertex, 1.00 );
                ShareUV = InputUV;
                ShareColor = InputColor;

            }
        """ % MMDPY_MATERIAL_USING_BONE_NUM

        fragment_shader_src = """
            #version 110
            uniform     sampler2D   Texture01;
            varying     vec2        ShareUV;
            varying     vec4        ShareColor;
            uniform     float       IsTexture;
            uniform     float       Alpha;
            void main( void )
            {
                vec4    color = texture2D( Texture01, ShareUV );
                color += (1.00 - IsTexture) * ShareColor;
                color.a = Alpha;
                gl_FragColor = color;
            }
        """
        self.program = glCreateProgram()
        if not self.createShader(GL_VERTEX_SHADER, vertex_shader_src):
            print('GL_VERTEX_SHADER ERROR')
            return False
        if not self.createShader(GL_FRAGMENT_SHADER, fragment_shader_src):
            print('GL_FRAGMENT_SHADER ERROR')
            return False
        else:
            if not self.link():
                print('SHADER LINK ERROR')
                return False
            self.createVariable()
            return True

    def createShader(self, shader_type, src):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, src)
        glCompileShader(shader)
        r = glGetShaderiv(shader, GL_COMPILE_STATUS)
        if r == 0:
            return False
        else:
            glAttachShader(self.program, shader)
            glDeleteShader(shader)
            return True

    def link(self):
        if self.program is not None:
            glLinkProgram(self.program)
        r = glGetProgramiv(self.program, GL_LINK_STATUS)
        if r == 0:
            glDeleteProgram(self.program)
            return False
        else:
            glGetProgramiv(self.program, GL_LINK_STATUS)
            glGetProgramiv(self.program, GL_LINK_STATUS)
            return True

    def createVariable(self):
        self.shaderOn()
        self.glsl_id_vertex = glGetAttribLocation(self.program, 'Vertex')
        self.glsl_id_uv = glGetAttribLocation(self.program, 'InputUV')
        self.glsl_id_color = glGetUniformLocation(self.program, 'InputColor')
        self.glsl_id_texture01 = glGetUniformLocation(self.program, 'Texture01')
        self.glsl_id_alpha = glGetUniformLocation(self.program, 'Alpha')
        self.glsl_id_is_texture = glGetUniformLocation(self.program, 'IsTexture')
        self.glsl_id_bone_indexes = glGetAttribLocation(self.program, 'BoneIndices')
        self.glsl_id_bone_weights = glGetAttribLocation(self.program, 'BoneWeights')
        self.glsl_id_bone_matrix = glGetUniformLocation(self.program, 'BoneMatrix')
        glActiveTexture(GL_TEXTURE0)
        glUniform1i(self.glsl_id_texture01, 0)
        self.shaderOff()
