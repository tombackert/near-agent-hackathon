from openai import OpenAI


client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  store=True,
  messages=[
    {"role": "user", "content": "write a pitch about a startup that uses AI to innovate"}
  ]
)

print(completion.choices[0].message);
