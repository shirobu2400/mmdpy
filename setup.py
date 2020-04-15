from setuptools import setup

setup(
    name="mmdpy",
    version="0.0.1",
    install_requires=[  "PyOpenGL",
                        "PyOpenGL_accelerate",
                        "numpy",
                        "Pillow"],
    extras_require={
        "develop": [   "PyOpenGL",
                        "PyOpenGL_accelerate",
                        "numpy",
                        "Pillow"]
    }
)
