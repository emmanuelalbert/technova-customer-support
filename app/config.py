from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env variables into the environment.
# This allows Pydantic AI and Google Gemini to access them.
load_dotenv()


class Settings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    google_refresh_token: str

    database_url: str

    # Google Gemini API configuration
    google_api_key: str
    classifier_model: str = "google:gemini-2.5-flash"
    agent_model: str = "google:gemini-2.5-flash"

    poll_interval_seconds: int = 30

    dashboard_username: str = "admin"
    dashboard_password: str = ""


settings = Settings()
