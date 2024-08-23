from sqlalchemy.orm import Session
from api.db.models import BotResponse
from api.db.db_init import get_db

class ManagerDB:
    def __init__(self, db: Session):
        self.db = db

    def add_item(self, bot_type, url_document, model_response, src_lang=None, tgt_lang=None):
        # Create a new BotResponse object
        new_response = BotResponse(
            bot_type=bot_type,
            url_document=url_document,
            model_response=model_response,
            src_lang=src_lang,
            tgt_lang=tgt_lang
        )
        
        # Add the new response to the session and commit the transaction
        self.db.add(new_response)
        self.db.commit()
        self.db.refresh(new_response)  # Refresh to get the updated values like user_id

        return new_response

# Example usage (in a FastAPI route, for instance):
# from fastapi import Depends
# from .manager_db import ManagerDB
# from .db_init import get_db

# @app.post("/add-response")
# def add_response(bot_type: str, url_document: str, model_response: str, src_lang: str = None, tgt_lang: str = None, db: Session = Depends(get_db)):
#     db_manager = ManagerDB(db)
#     response = db_manager.add_item(bot_type, url_document, model_response, src_lang, tgt_lang)
#   
