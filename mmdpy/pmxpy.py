from typing import Union
from . import pmxpy_load
from . import pmxpy_adjust
from . import mmdpy_type


class mmdpyPmx:
    def __init__(self, filename: str = ""):
        self.pmd_flag = False
        if filename != "":
            self.load(filename)

    def load(self, filename: str) -> Union[None, mmdpy_type.mmdpyTypeModel]:
        data = pmxpy_load.load(filename)
        if not data:
            return None
        mmd_data = pmxpy_adjust.adjust(data)
        return mmd_data
