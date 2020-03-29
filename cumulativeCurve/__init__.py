VERSION = (0, 0, 1)
__version__ = ".".join([str(x) for x in VERSION])

from .interpolate import Interpolate
from .cumulativeCurve import CumulativeCurve,curveFromBin,curveFromBinCount,merge

