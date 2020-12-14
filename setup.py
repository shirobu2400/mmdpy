from setuptools import setup

setup(
    name="mmdpy",
    packages=["mmdpy"],
    version="0.0.1",
    license="MIT",
    author='shirobu2400',
    author_email='shirobuwq2400kskm@gmail.com',
    url='https://github.com/shirobu2400/mmdpy',
    description="mmd viewer @ python",
    install_requires=["PyOpenGL",
                    "PyOpenGL_accelerate",
                    "numpy",
                    "numpy-quaternion",
                    "pybullet",
                    "Pillow"]
)
