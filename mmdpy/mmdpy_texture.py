import OpenGL.GL as gl
from PIL import Image
import numpy as np
from typing import Union


class mmdpyTexture:

    def __init__(self, filename: Union[str, None] = None):
        if filename is not None:
            self.load(filename)

    def draw(self) -> None:
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.glsl_texture)
        gl.glEnable(gl.GL_TEXTURE_GEN_S)
        gl.glEnable(gl.GL_TEXTURE_GEN_T)
        gl.glTexGeni(gl.GL_S, gl.GL_TEXTURE_GEN_MODE, gl.GL_SPHERE_MAP)
        gl.glTexGeni(gl.GL_T, gl.GL_TEXTURE_GEN_MODE, gl.GL_SPHERE_MAP)

    def load(self, filename: str) -> Union[int, None]:
        try:
            image = Image.open(filename)
        except ValueError:
            return None
        else:
            image = image.convert('RGBA')
            image_data = np.array(list(image.getdata()), np.int8)
            self.glsl_texture = gl.glGenTextures(1)
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glBindTexture(gl.GL_TEXTURE_2D, self.glsl_texture)
            gl.glPixelStorei(gl.GL_UNPACK_ALIGNMENT, 1)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
            gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
            gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_DECAL)
            gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, image.size[0], image.size[1], 0,
                            gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, image_data)
            return self.glsl_texture
