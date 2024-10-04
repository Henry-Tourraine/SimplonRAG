import requests
from bs4 import BeautifulSoup
import pandas as pd
import threading
import concurrent.futures
import json
import os
import shutil

base_url = "https://gutenberg.org"


def get_table_from_page(url):
  """
  Gets information table about a book at the given url
  """
  try:
    r = requests.get(url, timeout=120)
    soup = BeautifulSoup(r.text, "html.parser")
    if soup is None:
      return None

    if "No ebook by that number." in soup.text:
      return None

    content = soup.find("a", string="Plain Text UTF-8")
    table = soup.find("table", class_="bibrec")
    if not table:
      return None
    data = {"full_text": f"{base_url}{content['href']}"} if content is not None else {}

    for row in table.select("tr"):
      header = row.find("th")  # Change to "th" if you want to capture headers
      d = row.find("td")  # Change to "th" if you want to capture header
      if (not header) or (not d):
        continue
      header_text = header.get_text(strip=True)

      data[header_text] = d.get_text(strip=True)  # Get the text from each column
    return data
  except Exception as e:
    print(url)
    print(e)
    raise Exception("error")


def get_library(start: int = 1, max_books: int = 5000):
  """
  Scraps Gutenberg books pages with multithreading.
  Uses files to save temporarly data to lower RAM usage.

  start : minimum is one
  max_books : maximum number of books on the platform
  """
  base_url = "https://gutenberg.org"
  page_template_url = f"{base_url}/ebooks/"
  final_books = []
  headers = []
  temp = "temp"
  counter = [0]

  if os.path.exists(temp):
    shutil.rmtree(temp)
  os.makedirs(temp, exist_ok=True)

  def fetch_books(i:int, max=max_books, path=None):
    """
    Scraps Guttenberg books
    """
    try:
      if counter[-1] >= max:
        return final_books

      data = get_table_from_page(page_template_url + str(i) if path is None else base_url + path)
      if data is not None:
        counter.append(counter[-1] + 1)

        with open(os.path.join(temp, f"{i}.json"), "a") as f:
          f.write(json.dumps(data))
    except Exception as e:
      print(e)

  df = None
  with concurrent.futures.ThreadPoolExecutor(max_workers=1024) as executor:
      tasks = []
      i = start
      while counter[-1] < max_books:
        task = executor.submit(fetch_books, i)
        tasks.append(task)
        print(counter[-1])
        i += 1

      for task in concurrent.futures.as_completed(tasks):
            task.result()

      data = []
      for file in os.listdir(temp):
        with open(os.path.join(temp, file), "r") as f:
          lines = "".join(f.readlines())
          data.append(json.loads(lines))

      df = pd.DataFrame(data)
      return df

if __name__ == "__main__":
  # Attention au nombre de thread, pour ne pas bloquer sa machine
  df = get_library()
  df.to_csv("gutenberg.csv")
  print(df.head())