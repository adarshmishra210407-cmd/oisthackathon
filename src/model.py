import os
from groq import Groq

class Model:
    def __init__(self, model_choice="Groq", specific_model=""):
        # We now only use Groq as the default provider
        api_key = os.environ.get("GROQ_API_KEY", "")
        self.groq_client = Groq(api_key=api_key)
        self.specific_model = specific_model or "llama-3.3-70b-versatile"

    def generate(self, prompt, context):
        full_prompt = f"{prompt}\n\nTranscript:\n{context}"
        
        try:
            completion = self.groq_client.chat.completions.create(
                model=self.specific_model,
                messages=[{"role": "user", "content": full_prompt}],
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Groq AI Error: {str(e)}"
