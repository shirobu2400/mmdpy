import struct
import os
import types
from . import pmdpy_load
from . import pmdpy_adjust

class mmdpyPmd:

    def __init__(self, filename=None):
        self.pmd_flag = False
        if filename is not None:
            self.load(filename)

    def load(self, filename):
        r = pmdpy_load.load(self, filename)
        if not r:
            return False
        else:
            r = pmdpy_adjust.adjust(self)
            if not r:
                return False
            return True

