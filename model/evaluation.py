import pandas as pd
from pipeline import Pipeline

class QA:
  """
  class to store question and answer
  """
  def __init__(self, question: str = None, answer: str = None, match_: bool = None):
    self.question = question
    self.answer = answer
    self.match_ = match_

  def __str__(self):
    return f"Question: {self.question}\nAnswer: {self.answer}\nMatch: {self.match}"




def evaluate():
  """
  Tests the agent on 200 programmatically generated questions.
  """
  df = pd.read_csv("gutenberg.csv")
  df = df[~df["Summary"].isna()]
  df = df[(~df["Author"].isna()) & (~df["Title"].isna())]
  
  qas1 = [QA(f"Quel est l'auteur de {row['Title']} ?", row["Author"], False) for index, row in df.sample(n=100).iterrows()]
  qas2 = [QA(f"Dans quelle langue a été rédigé {row['Title']} ?", row["Language"], False) for index, row in df.sample(n=100).iterrows()]

  qas = qas1 + qas2
  retrieval_agent = Pipeline()
  for qa in qas:
    answer = retrieval_agent.prompt(qa.question)
    if qa.answer == answer:
      qa.match_ = True

  print(f"Score of agent is : {pd.Series([qa.match_ for qa in qas]).sum()}/{len(qas)}")
  return pd.Series([qa.match_ for qa in qas]).sum() / len(qas)


if __name__ == "__main__":
  evaluate()