from utils.load_config import load_config
import os

current_path = os.getcwd()
cfg_path = os.path.join(current_path, "config.yaml")
config_all = load_config(url= cfg_path)


CFG_MODBUS      = config_all['CFG_MODBUS']
CFG_REDIS       = config_all['CFG_REDIS']
CFG_SOCKET      = config_all['CFG_SOCKET']
CFG_SERVER      = config_all['CFG_SERVER']


DOCK_CONFIGS = {
    dock: {**config_all[f'MISSION_{dock}'], 'name': f'MISSION_{dock}'}
    for dock in ["A1", "A2", "A3", "O1", "O2", "O3", "M1", "M2", "M3", "M4"]
    # for dock in ["M1", "M2", "M3", "M4"]
}

# url_agv = 'http://172.20.10.3:24249'
url_gms = 'http://192.168.31.250:24249'
url_rms = 'http://192.168.31.250:8895'