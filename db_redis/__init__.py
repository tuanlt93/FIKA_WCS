from db_redis.handle_redis import RedisCache
from config.constants import HandlePalletConfig

redis_cache = RedisCache()

temp_number_carton_dws = redis_cache.hget(HandlePalletConfig.NUMBER_CARTON_OF_PALLET, HandlePalletConfig.QUANTITY_FROM_DWS)

if  temp_number_carton_dws is None:
    redis_cache.hset(HandlePalletConfig.NUMBER_CARTON_OF_PALLET, HandlePalletConfig.QUANTITY_FROM_DWS, 0)