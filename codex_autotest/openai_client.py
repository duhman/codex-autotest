import os
import time
from functools import lru_cache

def _get_api_key():
    key = os.getenv('OPENAI_API_KEY')
    if not key:
        raise EnvironmentError('OPENAI_API_KEY is not set')
    return key

@lru_cache(maxsize=128)
def chat_completion(prompt, model='gpt-3.5-turbo', max_tokens=1024, retries=3, backoff=1):
    """
    Send a chat completion request with retries and caching.
    Caches responses by (prompt, model, max_tokens).
    """
    import openai
    api_key = _get_api_key()
    openai.api_key = api_key
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=max_tokens,
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            last_exc = e
            if attempt < retries:
                time.sleep(backoff * (2 ** (attempt - 1)))
            else:
                raise
    # fallback
    raise last_exc