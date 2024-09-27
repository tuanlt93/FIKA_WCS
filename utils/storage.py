import yaml, os

class StorageH:
    """
    Read setting from yaml file once at start, support save data to file.
    """

    def __init__(self, file_path: str):
        self.path = file_path

        if not os.path.isfile(self.path):
            with open(self.path, 'a') as f:
                pass
        with open(self.path, 'r') as f:
            self.data = yaml.safe_load(f)
        
        if not self.data:
            self.data = {}
      
    def merge(self, dec, sto):
        if type(dec) != type(sto):
            return dec
        elif not isinstance(dec, dict):
            return sto
        
        dec = dict(dec)
        for key in dec:
            if key in sto:
                dec[key] = self.merge(dec[key], sto[key])
            
        return dec

    def store(self):
        """
        Write to file yaml
        """
        with open(self.path, 'w') as f:
            yaml.dump(self.data, f)

    def retrieve(self, format: dict):
        """
        Put data to format
        """
        return self.merge(format, self.data)
    
    def update(self, data: dict):
        '''
        New key will be added
        Existed key will be modified
        '''
        self.data.update(data)

    def safeUpdate(self, data: dict):
        '''
        New key will be added
        Existed key:
            if value in different format
            then not change
            else update value
        '''
        self.data = self.merge(self.data, data)
    
    def pop(self, key: str):
        """
        Remove a key-value
        """
        if key in self.data:
            self.data.pop(key)



# storage = StorageH('config.yaml')

# current_data = storage.retrieve({'key1': 'default_value'})

# storage.update({'key5': 'new_value'})

# storage.safeUpdate({'key6': 'new_value'})  # Sẽ không cập nhật nếu giá trị mới khác kiểu dữ liệu

# storage.store()


# storage.pop('key5')
# storage.store()

# storage = StorageH('config.yaml')
# storage.data = {
#     'key1': 'value1',
#     'key2': 'value2',
#     'key3': 'value3'
# }

# # self.data.pop(key)
# storage.data.pop('key2')  

# # self.pop(key)
# storage.pop('key3')  
