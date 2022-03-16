from setuptools import setup
import sys

if sys.version_info < (3, 9):
    sys.exit('Sorry, Python < 3.9 is not supported')

with open("./requirements.txt") as fp:
    packages = fp.readlines()
    packages = [p.replace("\n", "") for p in packages]

setup(
    name="mmdpy",
    packages=["mmdpy", "mmdpy_world"],
    version="0.0.1",
    license="MIT",
    author='shirobu2400',
    author_email='shirobuwq2400kskm@gmail.com',
    url='https://github.com/shirobu2400/mmdpy',
    description="mmd viewer @ python",
    install_requires=packages
)
