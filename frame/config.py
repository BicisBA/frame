import youconfigme as ycm

from frame.constants import Environments

cfg = ycm.AutoConfig()

env = cfg.env(default=Environments.DEV.value)
