import openai
from openai import OpenAI
from survey import Survey
import json

client = OpenAI()

class SurveyAgent:
    def __init__(self):
        self.surveys = []

    def generate_survey(self, topic: str) -> Survey:
        """
        Uses GPT-4o-mini to generate a survey for a given topic.
        """
        prompt = f"""
        Create a survey on the topic "{topic}".
        The survey should have the following structure:

        1. Title: A short, concise title (maximum 5 words).
        2. Introduction: A brief introduction (1–2 sentences) that introduces the topic.
        3. Questions: A list of 3–5 questions. Each question should include three short answer options.

        Ensure you output strictly valid JSON following this structure:
        {{
          "title": <Survey Title>,
          "introduction": <Brief introduction>,
          "questions": [
              {{
                "question": <Question text>,
                "options": [{{"option": <Answer option>}}, ...]
              }},
              ...
          ]
        }}
        """
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": topic}
        ]
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                store=True,
                messages=messages,
                response_format=Survey,
            )
            survey = response.choices[0].message.content
            
            return survey
        except Exception as e:
            print(f"An error occurred during survey generation: {e}")
            return None

    def update_survey(self, survey: Survey, modifications: str) -> Survey:
        """
        Uses GPT-4o-mini to modify the given survey according to the provided instructions.
        """
        edit_prompt = f"""
        Here is an existing survey:
        {survey}

        Please update the survey based on the following modifications:
        {modifications}

        Output the updated survey in strictly valid JSON format adhering the same structure.
        """
        messages = [
            {"role": "system", "content": "You are a survey editing assistant using GPT-4o-mini."},
            {"role": "user", "content": edit_prompt}
        ]
        try:
            response = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                store=True,
                messages=messages,
                response_format=Survey,
            )
            updated_survey = response.choices[0].message.content
            
            return updated_survey
        except Exception as e:
            print(f"An error occurred during survey modification: {e}")
            return survey

    def analyze_survey(self, survey: Survey) -> dict:
        pass
        
    def save_survey(self, survey: str, filename: str):
        """Parses the survey JSON string and saves it in a compact format (without newline characters)."""
        try:
            survey_dict = json.loads(survey)
        except Exception as e:
            print("Error parsing survey JSON:", e)
            return

        with open(filename, "w") as f:
            json.dump(survey_dict, f, separators=(',', ':'))