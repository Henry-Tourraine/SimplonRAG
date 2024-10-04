**Write .env file at root**
```
    AZURE_OPENAI_API_KEY=...
    AZURE_OPENAI_API_ENDPOINT=...
    AZURE_OPENAI_DEPLOYMENT_NAME=...
```
**Download gutenberg.csv either by scraping.py or import file manually and put it in /model folder**
*** To start ***
```
    uvicorn main:app --reload
```

*** To evaluate ***
```
    cd model
    python evaluation.py
```