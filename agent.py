import os.path
import json
import collections

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from openai import OpenAI
from survey import Survey

client = OpenAI()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
MY_SPREADSHEET_ID = "1vi8yPHNMTOBF6NtuqniwoN42juEfzgzF4M1i4N7NElA"
MY_RANGE_NAME = "Formularantworten 1!A:C"

class SurveyAgent:
    
    def __init__(self):
        self.surveys = []
        self.chat_history = []

    def add_to_chat_history(self, role:str , content: str):
        """Adds a message to the chat history."""
        self.chat_history.append({"role": role, "content": content})
        self.save_chat_history("chat_history.json")

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
            self.add_to_chat_history("assistant",json.loads(survey))
            
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
            self.add_to_chat_history("assistant", json.loads(updated_survey))
            
            return updated_survey
        except Exception as e:
            print(f"An error occurred during survey modification: {e}")
            return survey
        
    def save_survey(self, survey: str, filename: str):
        """Parses the survey JSON string and saves it in a compact format (without newline characters)."""
        try:
            survey_dict = json.loads(survey)
        except Exception as e:
            print("Error parsing survey JSON:", e)
            return

        with open(filename, "w") as f:
            json.dump(survey_dict, f, separators=(',', ':'))
    
    
    def save_chat_history(self, filename: str):
        """Saves the chat history in JSON format."""
        try:
            with open(filename, "w") as f:
                json.dump(self.chat_history, f, separators=(',', ':'))
        except Exception as e:
            print("Error saving chat history JSON:", e)
    
    
    def fetch_and_aggregate_responses(self, survey_title: str, survey_description: str) -> dict:
        """
        Fetch responses from the Google Sheet, aggregate them, and return the data in the desired format.
        """
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        try:
            service = build("sheets", "v4", credentials=creds)
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=MY_SPREADSHEET_ID,
                range=MY_RANGE_NAME
            ).execute()
            rows = result.get("values", [])
            if not rows:
                print("No data found.")
                return {}
            aggregated_data = self.aggregate_responses(rows, survey_title, survey_description)
            return aggregated_data
        except HttpError as err:
            print(err)
            return {}

    def aggregate_responses(self, rows, title, description) -> dict:
        """
        Aggregates the responses from the sheet rows.
        Assumption: The first row contains headers, where the first column (e.g. timestamp) is not evaluated.
        """
        if not rows or len(rows) < 2:
            return {"title": title, "description": description, "questions": []}
        
        header = rows[0]  # e.g. ["Column 1", "Question 1", "Question 2"]
        responses = rows[1:]  # Each row corresponds to a response
        questions = header[1:]  # Questions start from the second column
        analysis_list = []
        
        for i, question in enumerate(questions, start=1):
            counter = collections.Counter()
            for response in responses:
                if len(response) > i:
                    answer = response[i]
                    counter[answer] += 1
            
            total = sum(counter.values())
            distribution = []
            for option, count in counter.items():
                percentage = round((count / total) * 100, 2) if total > 0 else 0.0
                distribution.append({
                    "option": option,
                    "count": count,
                    "percentage": percentage
                })
            most_common_answer = counter.most_common(1)[0][0] if total > 0 else None
            
            analysis_list.append({
                "question": question,
                "analysis": {
                    "most_common_answer": most_common_answer,
                    "distribution": distribution
                }
            })
        
        return {
            "title": title,
            "description": description,
            "questions": analysis_list
        }
    
    def analyze_survey(self, survey: dict) -> dict:
        pass