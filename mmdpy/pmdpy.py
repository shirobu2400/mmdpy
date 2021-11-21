from typing import Union
from . import pmdpy_load
from . import pmdpy_adjust
from . import mmdpy_type


class mmdpyPmd:
    def __init__(self, filename: str = ""):
        self.pmd_flag = False
        if filename != "":
            self.load(filename)

    def load(self, filename: str) -> Union[None, mmdpy_type.mmdpyTypeModel]:
        pmd_data = pmdpy_load.load(filename)
        if not pmd_data:
            return None
        mmd_data = pmdpy_adjust.adjust(pmd_data)
        return mmd_data
