import os
import asyncio
import random
import weave
from typing import Optional

import time
from litellm import acompletion

from dotenv import load_dotenv
load_dotenv()

from openai import RateLimitError


MODEL_MAP = {
    # ---------- OpenAI ----------
    "gpt-4o":         "gpt-4o-2024-11-20",          # latest GA snapshot 
    "gpt-4o-mini":    "gpt-4o-mini",                # still works but being replaced by 4.1-mini
    "gpt-4o-audio":   "gpt-4o-audio-preview",       # multimodal/audio
    "gpt-4o-realtime":"gpt-4o-realtime-preview",
    "gpt-4.1":        "gpt-4.1-2025-04-14",
    "gpt-4.1-mini":   "gpt-4.1-mini-2025-04-14",
    "gpt-4.1-nano":   "gpt-4.1-nano-2025-04-14",    
    "gpt-4-turbo":    "gpt-4-turbo-2025-03-15",
    "o3":             "o3-2025-04-16",
    "o3-mini":        "o3-mini-2025-01-31",
    "o4-mini":        "o4-mini-2025-04-16",         

    # ---------- Anthropic ----------
    "claude-opus-4":      "claude-opus-4-20250514",
    "claude-sonnet-4":    "claude-sonnet-4-20250514",  
    "claude-3-7-sonnet":  "claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet":  "claude-3-5-sonnet-20240620",
    "claude-3-5-haiku":   "claude-3-5-haiku-latest",
    "claude-3-opus":      "claude-3-opus-20240229",
    "claude-3-sonnet":    "claude-3-sonnet-20240229",
    "claude-3-haiku":     "claude-3-haiku-20240307"
}


EXPONENTIAL_BASE = 2    


class MajorityVoteModel(weave.Model):
    model: weave.Model
    num_responses: int = 3
    
    @weave.op()
    async def predict(self, prompt: str):
        tasks = [self.model.predict(prompt) for _ in range(self.num_responses)]
        return await asyncio.gather(*tasks)


class LiteLLMModel(weave.Model):
    model_name: str
    system_prompt: Optional[str] = None
    temp: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.95
    max_retries: int = 3
    
    def __init__(self, **data):
        super().__init__(**data)
        # Add any additional initialization logic here
        if self.model_name not in MODEL_MAP:
            raise ValueError(f"Invalid model name: {self.model_name}")

        if self.model_name.startswith(("o1", "o3", "o4")):
            self.temp = None
            self.top_p = None
            self.max_tokens = None

    
    @weave.op()
    async def predict(self, prompt: str):
        delay = 2

        for i in range(self.max_retries):
            try:
                messages = []
                if self.system_prompt is not None:
                    messages.append({
                        "role": "system",
                        "content": self.system_prompt
                    })
                messages.append({
                    "role": "user",
                    "content": prompt
                })
                response = await acompletion(
                    model=MODEL_MAP[self.model_name],
                    messages=messages,
                    temperature=self.temp,
                    max_tokens=self.max_tokens,
                    top_p=self.top_p
                )

                if response.choices[0].message.content is not None:
                    return response.choices[0].message.content
                else:
                    print(response)
                    raise Exception("No content in response")
            except RateLimitError as e:
                delay *= EXPONENTIAL_BASE * (1 + random.random())
                print(
                    f"RateLimitError, retrying after {round(delay, 2)} seconds, {i+1}-th retry...", e
                )
                await asyncio.sleep(delay)
                continue
            except Exception as e:
                print(f"Error in retry {i+1}, retrying...", e)
                continue

        raise Exception("Failed to get response after max retries")
