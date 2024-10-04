import logging
from fastapi import FastAPI
from DTOs import PromptDTO
from model import Pipeline

# Create the FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set log level to INFO
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
    handlers=[logging.StreamHandler()]  # Stream logs to stdout
)

logger = logging.getLogger("my_fastapi_app")

@app.get("/")
async def root():
    logger.info("Root endpoint was called")
    return {"message": "Hello from gutenbergGPT"}



@app.get("/prompt")
async def read_item(prompt: PromptDTO):
    logger.info(f"Prompt: {prompt.content}")
    p = Pipeline()
    response = p.prompt(prompt.content)
    logger.info(f"Response : {response}")
    return {"response": response}


