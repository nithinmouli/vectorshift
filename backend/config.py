import os

class Config:
    HUBSPOT_CLIENT_ID = os.getenv('HUBSPOT_CLIENT_ID', 'your_client_id_here')
    HUBSPOT_CLIENT_SECRET = os.getenv('HUBSPOT_CLIENT_SECRET', 'your_client_secret_here')
    HUBSPOT_REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
    
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    def validate_hubspot_config(self):
        return bool(self.HUBSPOT_CLIENT_ID and self.HUBSPOT_CLIENT_SECRET and 
                   self.HUBSPOT_CLIENT_ID != 'your_client_id_here' and 
                   self.HUBSPOT_CLIENT_SECRET != 'your_client_secret_here')

config = Config()
