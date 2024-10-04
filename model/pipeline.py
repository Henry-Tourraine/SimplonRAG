from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import AzureChatOpenAI
import os
import openai

class SingletonMeta(type):
    _instance = None  # Dictionary to store the single instance of the class
    
    def __call__(cls, *args, **kwargs):
        if cls._instance:
          return cls._instance  # Return the stored instance
        cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class Pipeline(metaclass=SingletonMeta):
    def __init__(self):
        prompt_template = """
        You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question.
        If you don't know the answer, just say that you don't know.

        Question: {question} 

        Context: {context}

        Answer:
        """

        store_path = "faiss"
        file = 'gutenberg.csv'

        store = None

        if os.path.exists(store_path):
            store = FAISS.load_local(store_path, OpenAIEmbeddings())
        else:
            loader = CSVLoader(file_path=file)
            data = loader.load()

        store = FAISS.from_documents(documents=data, embedding=OpenAIEmbeddings())
        store.save_local(store_path)

        prompt = ChatPromptTemplate.from_template(prompt_template)

        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        llm = AzureChatOpenAI(
            api_version="2023-05-15",
            deployment_name=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
            temperature=0
        )

        self.qa_chain = (
            {
                "context": store.as_retriever(search_kwargs={"k": 10}) | format_docs,
                "question": RunnablePassthrough(),
            }
            | prompt
            | llm
            | StrOutputParser()
        )


    def prompt(self, user_input: str):
        response = self.qa_chain.invoke(user_input)