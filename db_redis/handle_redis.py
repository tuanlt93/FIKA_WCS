import redis
import json
import redis.client
from config import CFG_REDIS
from utils.pattern import Singleton
from utils.logger import Logger

class RedisCache(metaclass= Singleton):
    def __init__(self, *args, **CFG_REDIS) -> None:
        """
        Initializes the connection parameters for the PLC station.

        Args:
            host: IP address of the redis (default: "127.0.0.1")
            port: redis port (default: 6379)
            db  : db port (default: 0)
        """
        self.host = CFG_REDIS.get('host', "127.0.0.1")
        self.port = CFG_REDIS.get('port', 6379)
        self.db = CFG_REDIS.get('db', 0)
        self.decode_responses = CFG_REDIS.get('decode_responses', True)

        self.redis_conn = redis.Redis(
            host=self.host, 
            port=self.port, 
            db=self.db, 
            decode_responses=self.decode_responses
        )
        if not self.redis_conn:
            Logger().error("Failed to connect to redis")
        try:
            self.redis_conn.ping()  # Ping Redis server to check connection
            Logger().info("Connect redis successful")
        except redis.ConnectionError:
            Logger().error("Failed to connect to redis")
            
    def get_connection(self):
        return self.redis_conn


    def set(self, key: str, value):
        if value is None: value = "Null"
        else: value = str(value)
        return self.redis_conn.set(key, value)
    
    def delete(self, key):
        return self.redis_conn.delete(key)
    
    def get(self, key: str):
        return self.redis_conn.get(key)
    
    def hset(self, topic: str, key: str, value):
        if value is None: value = "Null"
        else: value = str(value)
        return self.redis_conn.hset(topic, key, value)

    def hdel(self, topic: str, key: str):
        return self.redis_conn.hdel(topic, key)

    def hget(self, topic: str, key: str):
        return self.redis_conn.hget(topic, key)

    def hgetall(self, topic: str):
        return self.redis_conn.hgetall(topic)

    def sadd(self,group: str, topic: str):
        if topic is None: topic = "Null"
        else: topic = str(topic)
        return self.redis_conn.sadd(group, topic)
    
    def srem(self, group: str, topic: str):
        self.redis_conn.delete(topic)
        return self.redis_conn.srem(group, topic)
    
    def smembers(self, group: str):
        return self.redis_conn.smembers(group)


    
    def save_list_to_redis(self, key, list_of_dicts):
        """
        Chuyển từng từ điển thành chuỗi JSON và lưu vào Redis bằng lệnh RPUSH.
        """
        for item in list_of_dicts:
            self.redis_conn.rpush(key, json.dumps(item))

    def get_first_element(self, key):
        """
        Lấy phần tử đầu tiên từ danh sách trong Redis.
        đã chuyển đổi sang dict
        """
        first_element = self.redis_conn.lindex(key, 0)
        if first_element:
            return first_element
        return None
    
    def append_to_list(self, key, item: json):
        """
        Thêm một phần tử mới vào cuối danh sách trong Redis.

        Return:
            rpush(key, item)
        """
        self.redis_conn.rpush(key, item)


    def update_element_queue(self, topic: str, index: int, key: str, value):
        """  
            Chỉnh sửa dữ liệu thứ index trong queue
        """
        data = json.loads(self.redis_conn.lindex(name= topic, index= index))
        if data is None:
            print(f"No data found at index {index} in list {topic}")
            return None
        data[key] = value
        return self.redis_conn.lset(name= topic, index= index, value= json.dumps(data))


    def delete_first_element(self, key):
        """
        Xóa phần tử đầu tiên từ danh sách trong Redis.
        """
        self.redis_conn.lpop(key)
    
    def delete_all_element(self, key):
        """
        Xóa danh sách trong Redis.
        """
        self.redis_conn.delete(key)

    def get_all_elements(self, key):
        """
        Lấy tất cả phần tử trong danh sách từ Redis.
        """
        return [json.loads(item) for item in self.redis_conn.lrange(key, 0, -1)]

    def publisher(self, topic, message):
        """
        Publish a message to a Redis topic. 
        """
        return self.redis_conn.publish(topic, message)


    def subscriber(self, topic: str):
        """
        Subscribe to a Redis topic. (nên kiểm soát trong một thread riêng. Ít hiệu năng tiêu thụ)
        """
        self.redis_pubsub = self.redis_conn.pubsub()
        self.redis_pubsub.subscribe(topic)

    def listen(self) -> str:
        for message in self.redis_pubsub.listen():
            if message['type'] == 'message':
                return message["data"]

    
    # def subscriber(self, topic):
    #     """
    #     Nên sử dụng như subcriber ROS. Nhiều hiệu năng tiêu thụ.
    #     """
    #     self.pubsub.subscribe(topic)
    #     while True:
    #         message = self.pubsub.get_message()
    #         if message:
    #             data = message['data']
    #             if isinstance(data, bytes):
    #                 data = data.decode('utf-8')
    #             if data == 1:
    #                 continue
    #             else:
    #                 return data


    def update_element_by_name(self, key, name, new_age):
        """
        Tìm và cập nhật age của phần tử có name bằng giá trị name.
        """
        # Lấy danh sách từ Redis
        data_list = self.get_all_elements(key)
        # Tìm và cập nhật phần tử
        for index, item in enumerate(data_list):
            if item['name'] == name:
                item['age'] = new_age
                # Cập nhật phần tử tại vị trí index trong Redis
                self.redis_conn.lset(key, index, json.dumps(item))
                return True
        return False
    
    
    def closeRedis(self):
        return self.redis_conn.close()

    
    