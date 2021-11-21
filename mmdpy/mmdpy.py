# #### #### #### #### #### #### #### ####
# MMD Viewer on Python.
# Development by shirobu2400
# #### #### #### #### #### #### #### ####

import os
from . import mmdpy_bone
from . import pmdpy
from . import mmdpy_model
from . import mmdpy_motion
from . import vmd
from typing import Any, Dict, Union, cast


class motion:
    def __init__(self, model: mmdpy_model.mmdpyModel):
        self.motion_data: vmd.mmdpyVmd = vmd.mmdpyVmd()
        self.model = model
        self.frame: int = 0

    def load(self, filename: str) -> bool:
        if not self.motion_data.load(filename):
            # raise IOError
            return False
        self.motion = mmdpy_motion.mmdpyMotion(self.model, self.motion_data)
        return True

    def step(self, it: int = 1) -> None:
        for _ in range(it):
            self.frame += 1
            self.update()

    # モーション情報をモデルボーンに反映
    def update(self) -> None:
        self.motion.update(self.frame)


class model:
    def __init__(self, filename: str = ""):
        self.runnable: bool = False
        self.model: mmdpy_model.mmdpyModel = mmdpy_model.mmdpyModel()
        self.motion_data: Dict[str, motion] = {}
        if filename != "":
            if not self.load(filename):
                raise FileNotFoundError

    def load(self, filename: str) -> bool:
        self.filename: str = filename
        self.path, self.ext = os.path.splitext(filename)

        if self.ext == ".pmd" or self.ext == ".PMD":
            self.pmd_data = pmdpy.mmdpyPmd()
            self.data = self.pmd_data.load(self.filename)
            self.file_type = "pmd"
        elif self.ext == ".pmx" or self.ext == ".PMX":

            self.file_type = "pmx"
        else:
            print("Unknown file.")
            self.file_type = ""

        if not self.data:
            self.file_type = "None"
            return False
        self.model.set_model(self.data)
        self.model.update_bone()
        for b in self.model.bones:
            b.init_update_matrix()
        self.model.create_physics(self.data.physics_flag, self.data)

        self.runnable = True
        return True

    # 表示
    # 適応させるモーションがある場合 motio に入れる
    def draw(self) -> Any:
        if not self.runnable:
            return self

        self.model.update_bone()
        self.model.update_ik()
        # self.model.update_physics()
        self.model.draw()
        return self

    # モーション
    def motion(self, name: str) -> motion:
        if not self.runnable:
            raise RuntimeError
        if name not in self.motion_data:
            self.motion_data[name] = motion(self.model)
        return self.motion_data[name]

    # ボーンを取得
    def bone(self, p: Union[int, str]) -> mmdpy_bone.mmdpyBone:
        if not self.runnable:
            raise RuntimeError
        if type(p) == int:
            return self.model.get_bone(cast(int, p))
        if type(p) == str:
            return self.model.get_bone_by_name(cast(str, p))
        raise IndexError

    def bonetree(self) -> None:
        if not self.runnable:
            return None
        if len(self.model.bones) > 0:
            self.model.bones[0].print_childs()
