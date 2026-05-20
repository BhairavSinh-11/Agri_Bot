from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os
oauth = OAuth()

load_dotenv()

google = oauth.register(
        name='google',
        client_id=os.getenv("google_client_id"),
        client_secret=os.getenv("google_client_secret"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
)
