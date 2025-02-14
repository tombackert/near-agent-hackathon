from openai import OpenAI
import openai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

client = OpenAI()

def generate_survey(topic: str) -> str:
    prompt = f"""
      Create a survey on the topic "{topic}".
      The survey should have the following structure:

      1. **Title:** A short, concise title (maximum 5 words).
      2. **Introduction:** A brief introduction (1–2 sentences) that introduces the topic.
      3. **Questions:** A list of 3–5 questions. Each question should include three short and concise answer options.

      Please format the output as follows:

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
      """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

if __name__ == "__main__":
  print()
  print(" System Instructions ".center(100, "="))
  print()
  print("The survey will be generated with the following structure:")
  print("  - A concise title (max 5 words)")
  print("  - A brief introduction (1–2 sentences)")
  print("  - A list of 3–5 questions, each with 3 short answer options")
  print()
  print(" Survey Prompt ".center(100, "="))

  print()
  topic = input("Please enter the topic for the survey: ")
  print()
  survey = generate_survey(topic)
  print(" Generated Survey ".center(100, "="))
  print()
  print(survey)
  print()
  