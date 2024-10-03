from utils.load_config import load_config
import os

current_path = os.getcwd()
cfg_path = os.path.join(current_path, "config.yaml")
config_all = load_config(url= cfg_path)


CFG_MODBUS      = config_all['CFG_MODBUS']
CFG_REDIS       = config_all['CFG_REDIS']
CFG_SOCKET      = config_all['CFG_SOCKET']
CFG_SERVER      = config_all['CFG_SERVER']

CFG_MONGODB     = config_all['CFG_MONGODB']

URL_GMS         = config_all['CFG_RCS']['url_gms']
URL_RMS         = config_all['CFG_RCS']['url_rms']


INPUT_PALLET_CONFIGS = {
    dock: {**config_all[f'MISSION_{dock}'], 'name': f'MISSION_{dock}'}
    for dock in ["A1", "A2"]
}

INPUT_EMPTY_PALLET_CONFIGS = {
    dock: {**config_all[f'MISSION_{dock}'], 'name': f'MISSION_{dock}'}
    for dock in ["O3", "M4"]
}

OUTPUT_PALLET_CONFIGS = {
    dock: {**config_all[f'MISSION_{dock}'], 'name': f'MISSION_{dock}'}
    for dock in ["A3", "O1", "O2", "M1", "M2", "M3"]
}
