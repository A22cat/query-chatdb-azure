from dotenv import load_dotenv
import os

load_dotenv()

connection_string = (
    f"DRIVER={os.getenv('DB_DRIVER')};"
    f"SERVER={os.getenv('AZURE_SQL_SERVER')};"
    f"DATABASE={os.getenv('AZURE_SQL_DATABASE')};"
    f"UID={os.getenv('AZURE_SQL_USERNAME')};"
    f"PWD={os.getenv('AZURE_SQL_PASSWORD')}"
)
