class SharedInfo:
    api_key = None
    lastfm_base_url = None
    musicbrainz_base_url = None

    @classmethod
    def get_api_key(cls):
        return cls.api_key
    
    @classmethod
    def set_api_key(cls, key):
        cls.api_key = key
        
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
    