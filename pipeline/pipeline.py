import os

from src.vector_store import VectorStoreBuilder
from src.recommender import AnimeRecommender
from config.config import GROQ_API_KEY, MODEL_NAME
from utils.logger import get_logger
from utils.exception_handler import CustomException

logger = get_logger(__name__)


class AnimeRecommendationPipeline:
    def __init__(self, persist_dir="chroma_db", csv_path="data/anime_with_synopsis.csv"):
        try:
            logger.info("Intializing Recommdation Pipeline")

            self.persist_dir = persist_dir
            self.csv_path = csv_path
            vector_builder = VectorStoreBuilder(csv_path=self.csv_path, persist_dir=self.persist_dir)
            self._ensure_vector_store_is_ready(vector_builder)

            retriever = vector_builder.load_vector_store().as_retriever(search_kwargs={"k": 5})
            self.recommender = AnimeRecommender(retriever, GROQ_API_KEY, MODEL_NAME)

            logger.info("Pipleine intialized sucessfully...")

        except Exception as e:
            logger.error(f"Failed to intialize pipeline {str(e)}")
            raise CustomException("Error during pipeline intialization", e)

    def _ensure_vector_store_is_ready(self, vector_builder):
        db_path = os.path.join(self.persist_dir, "chroma.sqlite3")
        if not os.path.exists(db_path):
            logger.warning("Vector DB not found; building a fresh one from CSV.")
            vector_builder.build_and_save_vectorstore()
            return

        try:
            store = vector_builder.load_vector_store()
            result = store.get(limit=1)
            docs = result.get("documents", []) if isinstance(result, dict) else []
            if not docs:
                logger.warning("Vector DB is empty; rebuilding it from CSV.")
                vector_builder.build_and_save_vectorstore()
        except Exception as exc:
            logger.warning(f"Vector DB validation failed; rebuilding it. Error: {exc}")
            vector_builder.build_and_save_vectorstore()

    def recommend(self, query: str) -> str:
        try:
            logger.info(f"Recived a query {query}")

            recommendation = self.recommender.get_recommendation(query)

            logger.info("Recommendation generated sucesfully...")
        except Exception as e:
            logger.error(f"Failed to get recommendation {str(e)}")
            raise CustomException("Error during getting recommendation", e)
        else:
            logger.info(f"Recommendation: {recommendation}")
            return recommendation


if __name__ == "__main__":
    pipeline = AnimeRecommendationPipeline(persist_dir="chroma_db")
    user_query = "I'm looking for anime like bleach and naruto with a mix of action and adventure."
    recommendations = pipeline.recommend(user_query)
    print(recommendations)



        