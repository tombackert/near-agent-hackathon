import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

client = OpenAI()

class Option(BaseModel):
  option: str

class Item(BaseModel):
  question: str
  options: list[Option]
class Survey(BaseModel):
  title: str
  introduction: str
  questions: list[Item]



def generate_survey(topic: str) -> str:
  """Generates a survey based on a fixed template and user topic."""
  prompt = f"""
    Create a survey on the topic "{topic}".
    The survey should have the following structure:

    1. **Title:** A short, concise title (maximum 5 words).
    2. **Introduction:** A brief introduction (1–2 sentences) that introduces the topic.
    3. **Questions:** A list of 3–5 questions. Each question should include three short and concise answer options.

    Ensure to output it strictly in valid JSON format, using the following structure:

    Title: <Survey Title>
    Introduction: <Brief introduction>
    Questions:
    1. Question: <Question 1>
      - Option 1: <Answer 1>
      - Option 2: <Answer 2>
      - Option 3: <Answer 3>
    2. Question: <Question 2>
      - Option 1: <Answer 1>
      - Option 2: <Answer 2>
      - Option 3: <Answer 3>
    ... 

    Ensure that all answer options are truly short and concise.
    Make sure the output is valid JSON without any additional text.
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
  except Exception as e:
    print(f"An error occurred during generation: {e}")

  return survey

def edit_survey(survey: str, modifications) -> str:
  """
  Allows the user to iteratively modify the survey.
  The user can select specific parts (title, introduction, questions, answer options) to edit.
  The modifications are passed as instructions to the LLM, which returns the updated survey.
  """
  while True:

    edit_prompt = f"""
      The following is an existing survey:

      {survey}

      Based on the following instructions, update the survey accordingly:

      {modifications}

      Ensure to output it strictly in valid JSON format, and structure as provided.
      """
    
    messages = [
      {"role": "system", "content": f" You should update the given survey according to {edit_prompt}"},
      {"role": "user", "content": edit_prompt}
    ]

    try:
      response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        store=True,
        messages=messages,
        response_format=Survey,
      )
      survey = response.choices[0].message.content

    except Exception as e:
      print(f"An error occurred during update: {e}")
            
    return survey
  

def save_survey(survey: str, filename: str):
  """Parses the survey JSON string and saves it in a compact format (without newline characters)."""
  try:
      survey_dict = json.loads(survey)
  except Exception as e:
      print("Error parsing survey JSON:", e)
      return

  with open(filename, "w") as f:
      json.dump(survey_dict, f, separators=(',', ':'))



def run_survey_generator():
  """Runs the survey generator and enables post-generation edits."""
  
  print("\n" + " SURVEY GENERATOR ".center(100, "=") + "\n")
  
  topic = input("Enter survey topic: ").strip()
  print("Generating survey...")
  survey = generate_survey(topic)
  save_survey(survey, "survey.json")
  
  print("\n" + " Start of Generated Survey ".center(100, "=") + "\n")
  print(survey)
  print("\n" + " End of Generated Survey ".center(100, "=") + "\n")

  while True:
    edit_choice = input("Edit survey? (yes/no): ").strip().lower()
    if edit_choice in ["yes", "y"]:
      modifications = input("Enter modifications: ").strip()
      print("Updating survey...")
      survey = edit_survey(survey, modifications)
      save_survey(survey, "survey.json")

      print("\n" + " Start of Generated Survey ".center(100, "=") + "\n")
      print(survey)
      print("\n" + " End of Generated Survey ".center(100, "=") + "\n")
    elif edit_choice in ["no", "n"]:
      print("User wants no further edits")
      save_survey(survey, "survey.json")
      print("Exiting generator..." + "\n")
      
      break

if __name__ == "__main__":
  run_survey_generator()