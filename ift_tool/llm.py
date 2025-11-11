import os
import warnings
from typing import Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# Suppress SSL warnings for local servers with self-signed certificates
warnings.filterwarnings("ignore", message="Unverified HTTPS request")
warnings.filterwarnings("ignore", category=UserWarning, module="httpx")
try:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass  # urllib3 might not be directly available, but that's okay

load_dotenv()

T = TypeVar("T", bound=BaseModel)


class OpenAIGenerator:
    def __init__(self, use_fireworks=False):
        if use_fireworks:
            base_url = os.getenv("FIREWORKS_API_BASE", "")
            # Disable SSL verification for local servers (self-signed certificates)
            # Only disable if connecting to a local IP address
            if base_url and (
                "localhost" in base_url
                or "127.0.0.1" in base_url
                or "10." in base_url
                or "192.168." in base_url
            ):
                http_client = httpx.Client(verify=False)
            else:
                http_client = None

            self.client = OpenAI(
                api_key=os.getenv("FIREWORKS_API_KEY"),
                base_url=base_url,
                http_client=http_client,
            )
        else:
            self.client = OpenAI(base_url="http://localhost:1234/v1")

    def generate_text(
        self, prompt="", model_name=os.getenv("FIREWORKS_MODEL"), **kwargs
    ):
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return response.choices[0].message.content

    def generate_json(
        self,
        model=os.getenv("FIREWORKS_MODEL"),
        prompt="",
        json_model: Type[T] = None,
        **kwargs,
    ) -> BaseModel:
        response = self.client.beta.chat.completions.parse(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format=json_model,
            temperature=0,
            **kwargs,
        )
        print(response)
        return response
