import OpenGL.GL as gl
from PIL import Image
import numpy as np
from typing import Union, Any
import os


class mmdpyTexture:
    def __init__(self, filename: Union[str, None] = None):
        self.glsl_texture = None
        if filename is not None:
            self.load(filename)

    def draw(self) -> None:
        if self.glsl_texture is None:
            return
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.glsl_texture)
        gl.glEnable(gl.GL_TEXTURE_GEN_S)
        gl.glEnable(gl.GL_TEXTURE_GEN_T)
        gl.glTexGeni(gl.GL_S, gl.GL_TEXTURE_GEN_MODE, gl.GL_SPHERE_MAP)
        gl.glTexGeni(gl.GL_T, gl.GL_TEXTURE_GEN_MODE, gl.GL_SPHERE_MAP)

    def load(self, filename: str) -> Union[int, None]:
        if not os.path.isfile(filename):
            return None

        image = Image.open(filename)
        image_channel = gl.GL_RGBA
        if image.mode != "RGBA":
            image_channel = gl.GL_RGB
        image_array = np.asarray(image).reshape(image.size[1], image.size[0], -1)
        return self.load_from_image(image_array, image_channel=image_channel)

    def load_from_image(self, image: np.ndarray, image_channel: Any = gl.GL_RGBA) -> Union[int, None]:
        if image is None:
            return None
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
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, image.shape[1], image.shape[0], 0,
                        image_channel, gl.GL_UNSIGNED_BYTE, image)
        return self.glsl_texture
