import OpenGL.GL as gl
import OpenGL.GLU as glu
import glfw
from typing import cast, List, Any
import time
import queue


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

    def elapsed_time(self) -> float:
        self.time_queue.put(time.time())
        if not self.time_queue.full():
            return 0
        top_time = self.time_queue.get()
        elapsed_time = (time.time() - top_time) / self.length
        return elapsed_time


class world:
    def __init__(self, window_name: str, window_width: int, window_height: int):
        self.window_name: str = window_name
        self.window_width: int = window_width
        self.window_height: int = window_height

        self.fps_calc: fpsCalculator = fpsCalculator()
        self.models: List[Any] = []

        # Initialize GLFW
        if not glfw.init():
            print('Failed to create glfw')
            raise RuntimeError

        # Create window
        self.window = glfw.create_window(self.window_width, self.window_height, self.window_name, None, None)
        if not self.window:
            glfw.terminate()
            print('Failed to create window')
            raise RuntimeError

        glfw.make_context_current(self.window)

        # resize callback function
        glfw.set_window_size_callback(self.window, self.resize)

    def push(self, model: Any) -> None:
        self.models.append(model)

    def resize(self, window, window_width: int, window_height: int):
        self.window = window
        self.window_width = window_width
        self.window_height = window_height

        """callback function resize window"""
        gl.glViewport(0, 0, self.window_width, self.window_height)
        # gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        glu.gluPerspective(45.0, float(self.window_width) / float(self.window_height), 0.10, 160.0)

    def run(self) -> bool:
        """run is main method.

        Returns:
            bool: return True if thw window is closed, false otherwise.
        """
        if glfw.window_should_close(self.window):
            return True

        # Set matrix mode
        gl.glClear(cast(int, gl.GL_COLOR_BUFFER_BIT) | cast(int, gl.GL_DEPTH_BUFFER_BIT))
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()

        # set perspective
        glu.gluPerspective(45.0, float(self.window_width) / float(self.window_height), 0.10, 160.0)

        # set camera
        glu.gluLookAt(0.0, 10.0, -30.0, 0.0, 10.0, 0.0, 0.0, 1.0, 0.0)

        # Render here, e.g. using pyOpenGL
        for model in self.models:
            model.draw()

        # enforce OpenGL command
        gl.glFlush()

        # Swap front and back buffers
        glfw.swap_buffers(self.window)

        # Poll for and process events
        glfw.poll_events()

        # wait
        glfw.wait_events_timeout(max(0.00, 1. / 60 - self.fps_calc.elapsed_time()))

        return False

    def close(self) -> None:

        # Destory window
        glfw.destroy_window(self.window)

        # finish GLFW
        glfw.terminate()
