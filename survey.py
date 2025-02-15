from pydantic import BaseModel

class Option(BaseModel):
  option: str

class Item(BaseModel):
  question: str
  options: list[Option]

class Survey(BaseModel):
  title: str
  introduction: str
  questions: list[Item]