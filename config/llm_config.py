from openai import OpenAI
import logging
from config.settings import settings

logger = logging.getlogger(__name__)

#Open AI Compatible API for SDK adoption
client = OpenAI(
    api_key = settings.OPENROUTER_API_KEY,
    base_url = settings.OPENROUTER_BASE_URL,
)

def generate_llm_output(prompt: str) -> str:
    try:
        responses = client.chat.completions.create(
            model = settings.LLM_MODEL,
            temperature = 0.2,
            messages = [
                {"role": "user", "content": prompt} 
            ]
        )

        return responses.choices[0].message.content
    
    except Exception as e:             
        
        logger.error(
            f"Primary model failed: {str(e)}"
        )
                      # noqa: F401
        print(
            f"Primary model has failed, let me check the exception or switching into an Fall Back model!"
            f"Switching to {settings.FALLBACK_MODEL}"
        )

        response = client.chat.completions.create(
            model = settings.FALLBACK_MODEL,
            temperature = 0.2,
            messages = [
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content