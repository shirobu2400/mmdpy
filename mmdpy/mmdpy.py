# #### #### #### #### #### #### #### ####
# MMD Viewer on Python.
# Development by shirobu2400
# #### #### #### #### #### #### #### ####

import os
from . import pmdpy
from . import mmdpy_model
from . import mmdpy_motion
from . import vmd

class motion:
    def __init__(self, model):
        self.motion_data = vmd.mmdpyVmd()
        self.model = model
        self.frame = 0

    def load(self, filename):
        if filename is None:
            return False
        if not self.motion_data.load(filename):
            return False
        self.motion = mmdpy_motion.mmdpyMotion(self.model, self.motion_data)
        return True

    def step(self, it=1):
        for _ in range(it):
            self.frame += 1
            self.update()

    # モーション情報をモデルボーンに反映
    def update(self):
        self.motion.update(self.frame)

class model:
    def __init__(self, filename=None):
        self.runnable = False
        self.model = mmdpy_model.mmdpyModel()
        self.motion_data = {}
        if filename is not None:
            if not self.load(filename):
                raise FileNotFoundError

    def load(self, filename):
        self.filename = filename
        self.path, self.ext = os.path.splitext(filename)

        if self.ext == ".pmd" or self.ext == ".PMD":
            self.data = pmdpy.mmdpyPmd()
            if not self.data.load(self.filename):
                return False
            self.file_type = "pmd"
        elif self.ext == ".pmx" or self.ext == ".PMX":

            self.file_type = "pmx"
        else:
            print("Unknown file.")
            self.file_type = ""
            return False

        self.model.setModel(self.data)
        self.updateBone()
        for b in self.model.bones:
            b.initUpdateMatrix()

        self.runnable = True
        return True

    def updateBone(self):
        if not self.runnable:
            return self
        for b in self.model.bones:
            b.updateMatrix(count_flag=True)
        for b in self.model.bones:
            b.initUpdateMatrix()

    def ik(self, ik_flag=True):
        if not self.runnable:
            return self
        if not ik_flag:
            return
        for b in [x for x in self.model.bones if x.ik is not None]:
            b.initUpdateMatrix()
            target = b.updateMatrix()[3, :3]
            b.ik.bone_to.move(target, chain=b.ik.child_bones, loop_size=b.ik.it)

    # 表示
    # 適応させるモーションがある場合 motio に入れる
    def draw(self):
        if not self.runnable:
            return self

        self.updateBone()
        self.ik()
        self.model.draw()
        return self

    # モーション
    def motion(self, name):
        if not self.runnable:
            return self
        if not name in self.motion_data:
            self.motion_data[name] = motion(self.model)
        return self.motion_data[name]

    # ボーンを取得
    def bone(self, p):
        if not self.runnable:
            return self

        if type(p) == int:
            return self.model.getBone(p)
        if type(p) == str:
            return self.model.getBoneByName(p)
        raise IndexError

    def bonetree(self):
        if not self.runnable:
            return self

        if len(self.model.bones) > 0:
            self.model.bones[0].printChilds()
