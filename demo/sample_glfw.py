import OpenGL.GL as gl
import OpenGL.GLU as glu
from typing import cast
import glfw
import mmdpy
import argparse


width = 640
height = 480


def main():

    # Set argment parsers
    parser = argparse.ArgumentParser(description="MMD model viewer sample.")
    parser.add_argument("-p", type=str, help="MMD model file name.")
    parser.add_argument("-v", type=str, help="MMD motion file name.")
    parser.add_argument("--bone", type=bool, default=False, help="Print bone informations.")
    args = parser.parse_args()

    # Initialize GLFW
    if not glfw.init():
        return

    # Create window
    window = glfw.create_window(width, height, 'mmdpy sample', None, None)
    if not window:
        glfw.terminate()
        print('Failed to create window')
        return

    # Create context
    # glfw.set_window_size_callback(window, window_size)
    # glfw.set_window_refresh_callback(window, window_refresh)
    glfw.make_context_current(window)

    # OpenGL Version
    print('Vendor :', gl.glGetString(gl.GL_VENDOR))
    print('GPU :', gl.glGetString(gl.GL_RENDERER))
    print('OpenGL version :', gl.glGetString(gl.GL_VERSION))

    # load argment
    model_name = args.p
    motion_name = args.v
    bone_information = args.bone
    print(model_name)
    print(motion_name)

    # Create mmdpy
    model = mmdpy.model()

    # load model
    if model_name is not None and not model.load(model_name):
        raise IOError("Model is not found")
    if bone_information:
        model.bonetree()

    # Load motion
    if motion_name != "" and not model.motion("vmd").load(motion_name):
        raise IOError("Motion is not found")

    while not glfw.window_should_close(window):
        # Set matrix mode
        gl.glClear(cast(int, gl.GL_COLOR_BUFFER_BIT) | cast(int, gl.GL_DEPTH_BUFFER_BIT))
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        if height == 0:
            continue

        # set perspective
        glu.gluPerspective(45.0, float(width) / float(height), 0.10, 160.0)

        # set camera
        glu.gluLookAt(0.0, 10.0, -30.0, 0.0, 10.0, 0.0, 0.0, 1.0, 0.0)

        # Render here, e.g. using pyOpenGL
        model.draw()

        # enforce OpenGL command
        gl.glFlush()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

        # wait
        glfw.wait_events_timeout(int(1000. / 60))

    # Destory window
    glfw.destroy_window(window)

    # finish GLFW
    glfw.terminate()


# Pythonのメイン関数はこんな感じで書きます
if __name__ == "__main__":
    main()