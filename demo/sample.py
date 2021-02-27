from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import sys
import time
import queue
import mmdpy
import argparse


class fpsCalculator:
    def __init__(self, length=30):
        self.time_queue = queue.Queue(maxsize=length)
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
RotationAxis = [0, 0, 0]
FPS = 60
fps_calc = fpsCalculator()

def display():
    """ display """
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    ## set camera
    # gluLookAt(0.0, 10.0, 80.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    gluLookAt(0.0, 10.0, -30.0, 0.0, 10.0, 0.0, 0.0, 1.0, 0.0)

    """  /**** **** **** **** **** **** **** ****/  """
    glPushMatrix()

    if model is not None:
        model.draw()

    glPopMatrix()
    """  /**** **** **** **** **** **** **** ****/  """
    # ##draw a teapot
    # glColor3f(0.0, 0.0, 0.0)

    # glPushMatrix()
    # glutSolidTeapot(2)  # solid
    # glPopMatrix()

    glFlush()  # enforce OpenGL command
    glutSwapBuffers()

def event(value):
    glutTimerFunc(1000 // FPS, event, value + 1)
    if model is not None:
        model.motion("vmd").step()
    fps_calc.show()
    glutPostRedisplay()

def reshape(width, height):
    """callback function resize window"""
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / float(height), 0.10, 160.0)

def init(width, height, model_name, motion_name):
    """ initialize """
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST) # enable shading

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    ##set perspective
    gluPerspective(45.0, float(width) / float(height), 0.10, 160.0)

    # モデリング変換
    glMatrixMode(GL_MODELVIEW)

    # 光源の色
    light_ambient = [0.25, 0.25, 0.25]
    light_diffuse = [1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0]

    # 光源の位置
    light_position = [0, 0, 2, 1]

    # 光源
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHTING)

    global model
    model = mmdpy.model()
    if model_name is not None and not model.load(model_name):
        print("model load error.")
        exit(0)
    model.bonetree()

    if motion_name is not None and not model.motion("vmd").load(motion_name):
        print("motion load error.")
        exit(0)

def main():
    window_width  = 600
    window_height = 600

    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_SINGLE | GLUT_DEPTH)
    glutInitWindowSize(window_width, window_height)         # window size
    glutInitWindowPosition(100, 100)                        # window position
    glutCreateWindow("mmdpy")                               # show window
    glutDisplayFunc(display)                                # draw callback function
    # glutIdleFunc(display)
    glutReshapeFunc(reshape)                                # resize callback function

    parser = argparse.ArgumentParser(description="MMD model viewer sample.")
    parser.add_argument("-p", type=str, help="MMD model file name.")
    parser.add_argument("-v", type=str, help="MMD motion file name.")
    args = parser.parse_args()

    model_name = args.p
    motion_name = args.v
    print(model_name)
    print(motion_name)
    init(window_width, window_height, model_name, motion_name)

    glutTimerFunc(1000 // FPS, event, 0)
    glutMainLoop()

if __name__ == '__main__':
    main()
