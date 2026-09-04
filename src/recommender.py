from langchain_classic.chains import RetrievalQA
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq

if __package__:
    from .prompt_template import get_anime_prompt
else:
    from prompt_template import get_anime_prompt

import os
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

class AnimeRecommender:
    def __init__(self,retriever, api_key:str, model_name:str):
        self.llm = ChatGroq(api_key=api_key, model=model_name, temperature=0)
        self.prompt = get_anime_prompt()

        self.qa_chain = RetrievalQA.from_chain_type(
            llm = self.llm,
            chain_type = "stuff",
            retriever = retriever,
            return_source_documents = True,
            chain_type_kwargs = {"prompt":self.prompt}
        )

    def get_recommendation(self,query:str):
        result = self.qa_chain({"query":query})
        return result['result']

if __name__ == "__main__":
    from langchain_classic.vectorstores import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    # Initialize the vector store and embeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory="db", embedding_function=embeddings)

    # Create an instance of AnimeRecommender
    recommender = AnimeRecommender(retriever=vectorstore.as_retriever(), api_key=GROQ_API_KEY, model_name="openai/gpt-oss-120b")

    # Example query
    user_query = "I'm looking for anime with strong female leads and a mix of action and romance."
    recommendations = recommender.get_recommendation(user_query)
    print(recommendations)