from db_redis.handle_redis import RedisCache
from config.constants import HandlePalletConfig, DeviceConfig

redis_cache = RedisCache()

temp_number_carton_dws = redis_cache.hget(HandlePalletConfig.NUMBER_CARTON_OF_PALLET, HandlePalletConfig.QUANTITY_FROM_DWS)
redis_cache.hset(
    DeviceConfig.STATUS_ALL_DEVICES,
    DeviceConfig.STATUS_DOCK_M4,
    DeviceConfig.DOCK_FULL,
)

if  temp_number_carton_dws is None:
    redis_cache.hset(HandlePalletConfig.NUMBER_CARTON_OF_PALLET, HandlePalletConfig.QUANTITY_FROM_DWS, 0)