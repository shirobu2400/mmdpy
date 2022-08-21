import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut
from typing import cast
import sys
import time
import queue
import mmdpy
import argparse


class fpsCalculator:
    def __init__(self, length: int = 30):
        self.time_queue: queue.Queue = queue.Queue(maxsize=length)
        self.length = length

    def show(self):
        self.time_queue.put(time.time())
        if not self.time_queue.full():
            return
        top_time = self.time_queue.get()
        elapsed_time = (time.time() - top_time) / self.length
        if elapsed_time < 1e-8:
            return
        # print("{0}[FPS], {1}[time]".format(1.00 / elapsed_time, elapsed_time))


model = None
bone_information = False
RotationAxis = [0, 0, 0]
FPS = 30
fps_calc = fpsCalculator()


def display():
    """ display """
    gl.glClear(cast(int, gl.GL_COLOR_BUFFER_BIT) | cast(int, gl.GL_DEPTH_BUFFER_BIT))
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    # set camera
    # gluLookAt(0.0, 10.0, 80.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    glu.gluLookAt(0.0, 10.0, -30.0, 0.0, 10.0, 0.0, 0.0, 1.0, 0.0)

    """  /**** **** **** **** **** **** **** ****/  """
    gl.glPushMatrix()

    if model is not None:
        model.draw()

    gl.glPopMatrix()
    """  /**** **** **** **** **** **** **** ****/  """

    gl.glFlush()  # enforce OpenGL command
    glut.glutSwapBuffers()


def event(value):
    global iteration
    glut.glutTimerFunc(1000 // FPS, event, value + 1)
    if model is not None:
        model.motion("vmd").step()
    fps_calc.show()
    glut.glutPostRedisplay()


def reshape(width, height):
    if width == 0 or height == 0:
        return
    """callback function resize window"""
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(45.0, float(width) / float(height), 0.10, 160.0)


def init(width, height, model_name, motion_name):
    if width == 0 or height == 0:
        return

    """ initialize """
    gl.glClearColor(0.0, 0.0, 1.0, 1.0)
    gl.glEnable(gl.GL_DEPTH_TEST)  # enable shading

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()

    # set perspective
    glu.gluPerspective(45.0, float(width) / float(height), 0.10, 160.0)

    # modeling transform
    gl.glMatrixMode(gl.GL_MODELVIEW)

    # light color
    light_ambient = [0.25, 0.25, 0.25]
    light_diffuse = [1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0]

    # light position
    light_position = [0, 0, 2, 1]

    # light setting
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, light_ambient)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, light_diffuse)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_SPECULAR, light_specular)
    gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, light_position)
    gl.glEnable(gl.GL_LIGHT0)
    gl.glEnable(gl.GL_LIGHTING)

    global model
    model = mmdpy.model()
    if model_name is not None and not model.load(model_name):
        print("model load error.")
        exit(0)

    global bone_information
    if bone_information:
        model.bonetree()

    if motion_name is not None and not model.motion("vmd").load(motion_name):
        print("motion load error.")
        exit(0)


def main():
    window_width = 600
    window_height = 600

    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(cast(int, glut.GLUT_RGB) | cast(int, glut.GLUT_SINGLE) | cast(int, glut.GLUT_DEPTH))
    glut.glutInitWindowSize(window_width, window_height)         # window size
    glut.glutInitWindowPosition(100, 100)                        # window position
    glut.glutCreateWindow("mmdpy")                               # show window
    glut.glutDisplayFunc(display)                                # draw callback function
    # glut.glutIdleFunc(display)
    glut.glutReshapeFunc(reshape)                                # resize callback function

    parser = argparse.ArgumentParser(description="MMD model viewer sample.")
    parser.add_argument("-p", type=str, help="MMD model file name.")
    parser.add_argument("-v", type=str, help="MMD motion file name.")
    parser.add_argument("--bone", type=bool, default=False, help="Print bone informations.")
    args = parser.parse_args()

    model_name = args.p
    motion_name = args.v
    global bone_information
    bone_information = args.bone
    print(model_name)
    print(motion_name)
    init(window_width, window_height, model_name, motion_name)

    glut.glutTimerFunc(1000 // FPS, event, 0)
    glut.glutMainLoop()


if __name__ == '__main__':
    main()
