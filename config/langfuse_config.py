from langfuse import LangFuse
from config.settings import settings

langfuse = LangFuse(
    public_key = settings.LANGFUSE.PUBLIC_KEY,
    secret_key = settings.LANGFUSE.SECRET_KEY,
    host = settings.LANGFUSE_HOST,
    base_url = settings.LANGFUSE_BASE_URL
)