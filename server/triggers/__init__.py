"""finds all the triggers in the trigger dir"""
from os.path import dirname, basename, isfile
import glob

MODULE_LIST = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in MODULE_LIST if isfile(f)]
