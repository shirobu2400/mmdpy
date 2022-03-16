# #### #### #### #### #### #### #### ####
# MMD Viewer on Python.
# Development by shirobu2400
# #### #### #### #### #### #### #### ####

import os
from . import mmdpy_bone
from . import pmdpy
from . import pmxpy
from . import mmdpy_model
from . import mmdpy_motion
from . import vmd
import numpy as np
from typing import Any, Dict, Union, cast


class motion:
    """Motion class
    Loaded Model motion.
    """
    def __init__(self, model: mmdpy_model.mmdpyModel):
        self.motion_data: vmd.mmdpyVmd = vmd.mmdpyVmd()
        self.model: mmdpy_model.mmdpyModel = model
        self.frame: int = 0
        self.motion: Union[None, mmdpy_motion.mmdpyMotion] = mmdpy_motion.mmdpyMotion(self.model, None)

    def load(self, filename: str) -> bool:
        """モーションの読み込み

        Args:
            filename (str): モーションのパス .vmd

        Returns:
            bool: 読み込み成功判定
        """
        if not self.motion_data.load(filename):
            # raise IOError
            return False
        self.motion = mmdpy_motion.mmdpyMotion(self.model, self.motion_data)
        return True

    def step(self, it: int = 1) -> None:
        """フレームをit分進める

        Args:
            it (int, optional): 進めるフレーム数. Defaults to 1.
        """
        for _ in range(it):
            self.update()
            self.frame += 1

    # モーション情報をモデルボーンに反映
    def update(self) -> None:
        """モーション情報をボーンに更新する"""
        if not self.motion:
            return
        self.motion.update(self.frame)

    # モーションの再生終了判定
    def finish(self) -> bool:
        """モーションの終了判定

        Returns:
            bool: モーションが終了でTrue, 続いている場合はFalse
        """
        if not self.motion:
            return True
        return self.motion.finish()

    # motion に反映する
    def reflection(self, it: int = 1) -> None:
        """移動したボーンをモーションフレームに登録する

        Args:
            it (int, optional): 進めるフレーム数. Defaults to 1.
        """
        if not self.motion:
            return
        for bone in self.model.bones:
            p = bone.get_position_delta()
            q = bone.get_quaternion_delta()
            self.motion.change_motion(bone.name, self.frame, p, q)
        self.frame += it

    # モーションを保存
    def save(self, filename: str) -> None:
        """モーションの保存

        Args:
            filename (str): 保存名 .vmd
        """
        if not self.motion:
            return
        vmd_connecter: vmd.mmdpyVmd = vmd.mmdpyVmd()
        motions = vmd_connecter.convert_vmd(self.motion)
        vmd_connecter.save(filename, motions)
        print(f"save motion. => {filename}")


class model:
    """Model class
    Attributes:
        runnable (bool): 実行可能状態であるか判定する
        model (mmdpy_model.mmdpyModel): モデル情報
        motion_data (Dict[str, motion]): 名前を付けたモーション
    """
    def __init__(self, filename: str = ""):
        self.runnable: bool = False
        self.model: mmdpy_model.mmdpyModel = mmdpy_model.mmdpyModel()
        self.motion_data: Dict[str, motion] = {}
        if filename != "":
            if not self.load(filename):
                raise FileNotFoundError

    def load(self, filename: str) -> bool:
        """"モデルのロード
        Args:
            filename (str): モデルファイルパス, pmd or pmx

        Return:
            bool: 読み込みの成功フラグ
        """
        self.filename: str = filename
        self.path, self.ext = os.path.splitext(filename)

        if self.ext == ".pmd" or self.ext == ".PMD":
            self.pmd_data = pmdpy.mmdpyPmd()
            self.data = self.pmd_data.load(self.filename)
            self.file_type = "pmd"
        elif self.ext == ".pmx" or self.ext == ".PMX":
            self.pmx_data = pmxpy.mmdpyPmx()
            self.data = self.pmx_data.load(self.filename)
            self.file_type = "pmx"
        else:
            print("Unknown file.")
            self.file_type = ""

        if not self.data:
            self.file_type = "None"
            return False
        self.model.set_model(self.data)
        self.model.update_bone()
        self.model.create_physics(self.data.physics_flag, self.data)

        self.runnable = True
        return True

    # 表示
    # 適応させるモーションがある場合 motion に入れる
    def draw(self) -> Any:
        """表示

        Returns:
            Any: 自身を返す

        """
        if not self.runnable:
            return self

        # self.model.update_physics()
        self.model.update_bone()
        self.model.draw()

        # bone 初期化
        for bone in self.model.bones:
            bone.add_matrix(np.identity(4), overwrite=True)
        return self

    # モーション
    def motion(self, name: str) -> motion:
        """モーションクラスを取得

        Args:
            name (str): モーション名

        Raises:
            RuntimeError: まだ実行可能でない場合例外を飛ばす

        Returns:
            motion: モーションクラス
        """
        if not self.runnable:
            raise RuntimeError
        if name not in self.motion_data.keys():
            self.motion_data[name] = motion(self.model)
        return self.motion_data[name]

    # ボーンを取得
    def bone(self, p: Union[int, str]) -> mmdpy_bone.mmdpyBone:
        """ボーンクラスを取得する

        Args:
            p (Union[int, str]): ボーンIDもしくは、ボーン名

        Raises:
            RuntimeError: 実行状態可能ではない
            IndexError: ボーンのIDもしくは、名前が不正

        Returns:
            mmdpy_bone.mmdpyBone: ボーンクラス
        """
        if not self.runnable:
            raise RuntimeError
        if type(p) == int:
            return self.model.get_bone(cast(int, p))
        if type(p) == str:
            return self.model.get_bone_by_name(cast(str, p))
        raise IndexError

    def bonetree(self) -> None:
        """ボーンの階層構造を出力"""
        if not self.runnable:
            return None
        if len(self.model.bones) > 0:
            self.model.bones[0].print_childs()
