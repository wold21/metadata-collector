class SharedInfo:
    api_key = None

    @classmethod
    def get_api_key(cls):
        return cls.api_key
    
    @classmethod
    def set_api_key(cls, key):
        cls.api_key = key