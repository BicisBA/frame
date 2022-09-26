import youconfigme as ycm

from frame.constants import Environments

cfg = ycm.AutoConfig()

env = cfg.env(default=Environments.DEV.value)

BA_BIKES_CREDS = {
    'client_id': cfg.ecobici.client_id(),
    'client_secret': cfg.ecobici.client_secret(),
}
