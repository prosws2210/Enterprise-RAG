from openai import OpenAI
from loguru import logger

from app.config import settings

openai_client = OpenAI(api_key=settings.openai_api_key)

groq_client = None
if settings.groq_api_key:
    groq_client = OpenAI(
        api_key=settings.groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )

def generate(system_prompt: str, user_message: str, model: str | None = None, temperature: float = 0.0) -> dict:
    if model is None:
        model = settings.llm_model_answer

    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
    except Exception as e:
        logger.warning(f"OpenAI completion failed: {e}. Falling back to Groq.")
        if groq_client is None:
            raise
        
        fallback_model = settings.groq_fallback_model
        response = groq_client.chat.completions.create(
            model=fallback_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )

    text = response.choices[0].message.content or ""

    usage = {
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0,
    }

    return {"text": text, "usage": usage}

def generate_with_json(
    system_prompt: str,
    user_message: str,
    model: str | None = None,
    temperature: float = 0.0,
) -> dict:

    if model is None:
        model = settings.llm_model_grader

    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.warning(f"OpenAI completion failed: {e}. Falling back to Groq.")
        if groq_client is None:
            raise
        
        fallback_model = settings.groq_fallback_model
        response = groq_client.chat.completions.create(
            model=fallback_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
            response_format={"type": "json_object"},
        )

    text = response.choices[0].message.content or ""
    usage = {
        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
        "total_tokens": response.usage.total_tokens if response.usage else 0,
    }
    return {"text": text, "usage": usage}