from PLC.plc_controller import PLCController
from db_redis import redis_cache
from config.constants import HandlePalletConfig, DeviceConfig, DeviceConnectStatus


redis_cache.hset(DeviceConnectStatus.CONNECTION_STATUS_ALL_DEVICE, DeviceConnectStatus.CONNECTION_STATUS_PLC, DeviceConnectStatus.DISCONNECT)

temp_number_carton_dws = redis_cache.hget(HandlePalletConfig.NUMBER_CARTON_OF_PALLET, HandlePalletConfig.QUANTITY_FROM_DWS)
redis_cache.hset(
    DeviceConfig.STATUS_ALL_DEVICES,
    DeviceConfig.STATUS_DOCK_REJECT,
    DeviceConfig.DOCK_EMPTY,
)

if  temp_number_carton_dws is None:
    redis_cache.hset(HandlePalletConfig.NUMBER_CARTON_OF_PALLET, HandlePalletConfig.QUANTITY_FROM_DWS, 0)


PLC_controller = PLCController()