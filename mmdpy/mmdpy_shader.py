from . import mmdpy_root
import OpenGL
import OpenGL.GL as gl
import numpy as np
from typing import Any, Union, List, cast
from . import mmdpy_type
MMDPY_MATERIAL_USING_BONE_NUM = mmdpy_root.MMDPY_MATERIAL_USING_BONE_NUM
OpenGL.ERROR_ON_COPY = True


class mmdpyShader:
    def __init__(self):
        self.program = None
        if not self.compile():
            raise IOError

    def draw(self, glsl_info: mmdpy_type.glslInfoClass) -> None:
        self.shader_on()
        gl.glUniform1f(self.glsl_id_is_texture, 0.00)
        if glsl_info.texture is not None:
            gl.glUniform1f(self.glsl_id_is_texture, 1.00)
            glsl_info.texture.draw()
        gl.glUniform4f(self.glsl_id_color,
                       glsl_info.color[0], glsl_info.color[1], glsl_info.color[2], glsl_info.color[3])
        gl.glUniform1f(self.glsl_id_alpha, glsl_info.alpha)
        gl.glUniformMatrix4fv(self.glsl_id_bone_matrix, int(glsl_info.matrices.shape[0]),
                              gl.GL_FALSE, cast(object, glsl_info.matrices))
        gl.glBindVertexArray(glsl_info.glsl_vao)
        gl.glDrawElements(gl.GL_TRIANGLES, glsl_info.face_size, gl.GL_UNSIGNED_SHORT, None)
        gl.glBindVertexArray(0)
        self.shader_off()

    def set_buffers(self, vertex: np.ndarray, uv: np.ndarray, face: np.ndarray) -> mmdpy_type.glslInfoClass:
        glsl_info = mmdpy_type.glslInfoClass()
        face_size = len(face)
        face = np.array(face, dtype=(np.uint16))
        glsl_vbo_vertex = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, glsl_vbo_vertex)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertex.nbytes, vertex, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        glsl_vbo_uv = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, glsl_vbo_uv)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, uv.nbytes, uv, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        glsl_vao = gl.glGenVertexArrays(1)
        gl.glBindVertexArray(glsl_vao)
        gl.glEnableVertexAttribArray(self.glsl_id_vertex)
        gl.glEnableVertexAttribArray(self.glsl_id_uv)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, glsl_vbo_vertex)
        gl.glVertexAttribPointer(self.glsl_id_vertex, 3, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, glsl_vbo_uv)
        gl.glVertexAttribPointer(self.glsl_id_uv, 2, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        glsl_vbo_face = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, glsl_vbo_face)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, face.nbytes, face, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
        glsl_info.glsl_vao = glsl_vao
        glsl_info.face_size = face_size
        return glsl_info

    def set_bone(self, glsl_info: mmdpy_type.glslInfoClass, indexes: np.ndarray, weights: np.ndarray) -> None:
        glsl_vbo_bone_indexes = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, glsl_vbo_bone_indexes)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, indexes.nbytes, indexes, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        glsl_vbo_bone_weigths = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, glsl_vbo_bone_weigths)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, weights.nbytes, weights, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(glsl_info.glsl_vao)
        gl.glEnableVertexAttribArray(self.glsl_id_bone_indexes)
        gl.glEnableVertexAttribArray(self.glsl_id_bone_weights)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, glsl_vbo_bone_indexes)
        gl.glVertexAttribPointer(self.glsl_id_bone_indexes, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, glsl_vbo_bone_weigths)
        gl.glVertexAttribPointer(self.glsl_id_bone_weights, 4, gl.GL_FLOAT, gl.GL_FALSE, 0, None)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindVertexArray(0)
        glsl_info.indexes = indexes
        glsl_info.weights = weights

    def set_texture(self, glsl_info: mmdpy_type.glslInfoClass, texture: Any) -> None:
        glsl_info.texture = texture

    def set_material(self, glsl_info: mmdpy_type.glslInfoClass,
                     material: mmdpy_type.mmdpyTypeMaterial) -> None:
        glsl_info.material = material
        glsl_info.alpha = material.alpha
        glsl_info.color = material.color
        glsl_info.alpha = glsl_info.alpha

    def set_boneMatrix(self, glsl_info: mmdpy_type.glslInfoClass, matrix: List[np.ndarray]) -> None:
        matrices = []
        for _ in range(MMDPY_MATERIAL_USING_BONE_NUM):
            matrices.append(matrix)

        glsl_info.matrices = np.array(matrices, dtype=(np.float32))

    def set_projection_matrix(self,
                              matrix: Union[None, np.ndarray] = None,
                              left: float = -0.5, right: float = 0.5,
                              top: float = -0.5, bottom: float = 0.5,
                              near: float = 1.0, far: float = 160.0):
        if matrix is None:
            matrix = self.perspective_matrix(left, right, top, bottom, near, far)
            # gl.glUniformMatrix4fv(self.glsl_id_projection_matrix, matrix)

    def perspective_matrix(self,
                           left: float, right: float,
                           top: float, bottom: float,
                           near: float, far: float) -> np.ndarray:
        dx = right - left
        dy = bottom - top
        dz = far - near
        matrix = np.array([16], dtype=np.float32)
        matrix[0] = 2.0 * near / dx
        matrix[5] = 2.0 * near / dy
        matrix[8] = (right + left) / dx
        matrix[9] = (top + bottom) / dy
        matrix[10] = -(far + near) / dz
        matrix[11] = -1.0
        matrix[14] = -2.0 * far * near / dz
        matrix[1] = matrix[2] = matrix[3] = matrix[4] = matrix[6] = matrix[7] = matrix[12] = matrix[13] = matrix[15] = 0
        return matrix

    def shader_on(self) -> bool:
        if self.program is not None:
            gl.glUseProgram(self.program)
        else:
            return False
        return True

    def shader_off(self) -> None:
        gl.glUseProgram(0)

    def compile(self) -> bool:
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
        """ % (MMDPY_MATERIAL_USING_BONE_NUM)

        fragment_shader_src = """
            #version 110
            uniform     sampler2D   Texture01;
            varying     vec2        ShareUV;
            varying     vec4        ShareColor;
            uniform     float       IsTexture;
            uniform     float       Alpha;

            void main( void )
            {
                vec4    tex_color = texture2D( Texture01, ShareUV );
                // tex_color += ( 1.00 - IsTexture ) * ShareColor;
                tex_color.a = tex_color.a * Alpha;
                //gl_FragColor = tex_color * ( 1.00 - ShareColor.a ) + ShareColor * ShareColor.a;
                gl_FragColor = tex_color * ( 1.00 - ShareColor.a ) + ShareColor * ShareColor.a;
            }
        """
        self.program = gl.glCreateProgram()
        if not self.create_shader(gl.GL_VERTEX_SHADER, vertex_shader_src):
            print('GL_VERTEX_SHADER ERROR')
            return False
        if not self.create_shader(gl.GL_FRAGMENT_SHADER, fragment_shader_src):
            print('GL_FRAGMENT_SHADER ERROR')
            return False
        else:
            if not self.link():
                print('SHADER LINK ERROR')
                return False
            self.create_variable()
            return True

    def create_shader(self, shader_type: Any, src: str) -> bool:
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, src)
        gl.glCompileShader(shader)
        r = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if r == 0:
            return False
        gl.glAttachShader(self.program, shader)
        gl.glDeleteShader(shader)
        return True

    def link(self) -> bool:
        if self.program is not None:
            gl.glLinkProgram(self.program)
        r = gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS)
        if r == 0:
            gl.glDeleteProgram(self.program)
            return False
        else:
            gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS)
            gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS)
            return True

    def create_variable(self) -> None:
        self.shader_on()
        self.glsl_id_vertex: int = gl.glGetAttribLocation(self.program, 'Vertex')
        self.glsl_id_uv: int = gl.glGetAttribLocation(self.program, 'InputUV')
        self.glsl_id_color: int = gl.glGetUniformLocation(self.program, 'InputColor')
        self.glsl_id_texture01: int = gl.glGetUniformLocation(self.program, 'Texture01')
        self.glsl_id_alpha: int = gl.glGetUniformLocation(self.program, 'Alpha')
        self.glsl_id_is_texture: int = gl.glGetUniformLocation(self.program, 'IsTexture')
        self.glsl_id_bone_indexes: int = gl.glGetAttribLocation(self.program, 'BoneIndices')
        self.glsl_id_bone_weights: int = gl.glGetAttribLocation(self.program, 'BoneWeights')
        self.glsl_id_bone_matrix: int = gl.glGetUniformLocation(self.program, 'BoneMatrix')
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glUniform1i(self.glsl_id_texture01, 0)
        self.shader_off()
