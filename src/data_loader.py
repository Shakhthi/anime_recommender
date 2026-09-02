import pandas as pd

class AnimeDataLoader:
    def __init__(self,original_csv:str,processed_csv:str):
        self.original_csv = original_csv
        self.processed_csv = processed_csv

    def load_and_process(self):
        df = pd.read_csv(self.original_csv , encoding='utf-8' , on_bad_lines='skip').dropna()

        required_cols = {'Name', 'Genres', 'sypnopsis'}

        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError("Missing column  in CSV File")
        
        df['combined_info'] = (
            "Title: " + df["Name"] + " Overview: " + df["sypnopsis"] + "Genres : " + df["Genres"]
        )

        df[['combined_info']].to_csv(self.processed_csv , index=False, encoding='utf-8')

        return self.processed_csv

if __name__ == "__main__":
    loader = AnimeDataLoader(original_csv="data/anime_with_synopsis.csv", processed_csv="data/processed_anime.csv")
    processed_file = loader.load_and_process()
    print(f"Processed data saved to: {processed_file}")
