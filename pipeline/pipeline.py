from src.vector_store import VectorStoreBuilder
from src.recommender import AnimeRecommender
from config.config import GROQ_API_KEY, MODEL_NAME
from utils.logger import get_logger
from utils.exception_handler import CustomException

logger = get_logger(__name__)

class AnimeRecommendationPipeline:
    def __init__(self, persist_dir="chroma_db"):
        try:
            logger.info("Intializing Recommdation Pipeline")

            vector_builder = VectorStoreBuilder(csv_path="", persist_dir=persist_dir)

            retriever = vector_builder.load_vector_store().as_retriever()

            self.recommender = AnimeRecommender(retriever, GROQ_API_KEY, MODEL_NAME)

            logger.info("Pipleine intialized sucessfully...")

        except Exception as e:
            logger.error(f"Failed to intialize pipeline {str(e)}")
            raise CustomException("Error during pipeline intialization" , e)
        
    def recommend(self,query:str) -> str:
        try:
            logger.info(f"Recived a query {query}")

            recommendation = self.recommender.get_recommendation(query)

            logger.info("Recommendation generated sucesfully...")
        except Exception as e:
            logger.error(f"Failed to get recommendation {str(e)}")
            raise CustomException("Error during getting recommendation" , e)
        else:
            logger.info(f"Recommendation: {recommendation}")
            return recommendation

if __name__ == "__main__":
    pipeline = AnimeRecommendationPipeline(persist_dir="chroma_db")
    user_query = "I'm looking for anime like bleach and naruto with a mix of action and adventure."
    recommendations = pipeline.recommend(user_query)



        