class SharedInfo:
    lastfm_api_key = None  # Last.fm 또는 공통 API 키
    lastfm_base_url = None
    musicbrainz_base_url = None
    theaudiodb_base_url = None
    theaudiodb_api_key = None  # TheAudioDB API 키 추가
    user_agent = "YourAppName/1.0 (gkstmdwo100@gmail.com)"  # 기본 User-Agent 설정
    elasticsearch_host = None
    elasticsearch_port = None

    @classmethod
    def get_lastfm_api_key(cls):
        return cls.lastfm_api_key
    
    @classmethod
    def set_lastfm_api_key(cls, key):
        cls.lastfm_api_key = key
        
    @classmethod
    def get_lastfm_base_url(cls):
        return cls.lastfm_base_url
    
    @classmethod
    def set_lastfm_base_url(cls, key):
        cls.lastfm_base_url = key
    
    @classmethod
    def get_musicbrainz_base_url(cls):
        return cls.musicbrainz_base_url
    
    @classmethod
    def set_musicbrainz_base_url(cls, key):
        cls.musicbrainz_base_url = key

    @classmethod
    def get_theaudiodb_base_url(cls):
        return cls.theaudiodb_base_url

    @classmethod
    def set_theaudiodb_base_url(cls, key):
        cls.theaudiodb_base_url = key

    @classmethod
    def get_theaudiodb_api_key(cls): 
        return cls.theaudiodb_api_key

    @classmethod
    def set_theaudiodb_api_key(cls, key):
        cls.theaudiodb_api_key = key
    
    @classmethod
    def get_user_agent(cls):
        return cls.user_agent
    
    @classmethod
    def set_user_agent(cls, agent):
        cls.user_agent = agent
        
    @classmethod
    def get_elasticsearch_host(cls):
        return cls.elasticsearch_host
    
    @classmethod
    def set_elasticsearch_host(cls, host):
        cls.elasticsearch_host = host
        
    @classmethod
    def get_elasticsearch_port(cls):
        return cls.elasticsearch_port
    
    @classmethod
    def set_elasticsearch_port(cls, port):
        cls.elasticsearch_port = port