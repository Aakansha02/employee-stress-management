import time
from pydantic import BaseModel
import google.generativeai as genai
import instructor


class GeminiClient:
    """
    A class to configure and interact with the Gemini model using InstructE for structured output.
    """

    def __init__(
        self,
        gemini_key: str,
        model_name: str = "gemini-1.5-flash",
        temperature: float = 0.1,
    ):
        """
        Initialize and configure the Gemini model client.

        Args:
            gemini_key (str): The API key for accessing the Gemini model.
            model (str): The selected Gemini model ("gemini-1.5-flash" or "gemini-1.5-pro")
        """
        self._configure_gemini_client(gemini_key, model_name, temperature)

    def _configure_gemini_client(self, gemini_key, model_name, temperature):
        """
        Configure the Gemini client using the provided API key.

        Args:
            gemini_key (str): The API key for Gemini model configuration.
            model (str): Gemini model name for Gemini model configuration.

        """
        genai.configure(api_key=gemini_key)
        self.client = instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name=model_name,
                generation_config=genai.GenerationConfig(temperature=temperature),
            ),
            mode=instructor.Mode.GEMINI_JSON,
        )

    def generate_response(
        self,
        prompt: str,
        structure: BaseModel,
        system_message: str = "You are my friend 'MOJO'.",
    ) -> BaseModel:
        """
        Generate a response from the Gemini model.

        Args:
            prompt (str): The input prompt for the model.
            structure (BaseModel): The expected response structure.

        Returns:
            BaseModel: The model's response.
        """
        time.sleep(4)
        response = self.client.chat.completions.create(
            # max_tokens=20000,
            messages=[
                {
                    "role": "system",
                    "content": system_message,
                },
                {"role": "user", "content": f"{prompt}. try to chear up the user"},
            ],
            response_model=structure,
        )

        return response
