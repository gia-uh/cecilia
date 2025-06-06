import os
from typing import Type, TypeVar
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)

class OpenAIGenerator():
    def __init__(self, use_fireworks=False):
        if use_fireworks:
            self.client = OpenAI(api_key=os.getenv("FIREWORKS_API_KEY"), base_url=os.getenv("FIREWORKS_API_BASE"))
        else:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_text(self, prompt= "", model_name = os.getenv("FIREWORKS_MODEL"), **kwargs):
        response = self.client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=False,
        )
        return response.choices[0].message.content

    def generate_json(self, model = os.getenv("FIREWORKS_MODEL"), prompt= "", json_model: Type[T] = None, **kwargs) -> BaseModel:
        response = self.client.beta.chat.completions.parse(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format=json_model,
            temperature=0,
            **kwargs,
        )
        print(response)
        return response
