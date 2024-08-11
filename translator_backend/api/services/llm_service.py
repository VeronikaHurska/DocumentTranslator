import json
from typing import List
import cohere
from api.settings import settings
from api.logger import logger
import ast


class LlmTranslator:
    def __init__(self, src_lang, tgt_lang):
        self.src_lang = src_lang
        self.tgt_lang = tgt_lang
        self.model = self.__init_model__()

    def __init_model__(self):
        if not settings.COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY is missing.")
        return cohere.Client(
            api_key=settings.COHERE_API_KEY,
        )

    def translate(self, text):
        logger.info(f'INPUT TEXT: {text}')
        prompt, chat_history = self._generate_prompt(
            self.src_lang, self.tgt_lang, text)
        response = self.model.chat(
            model=settings.cohere_model,
            message=prompt,
            chat_history=chat_history,
            temperature=0.0,
        )
        translated_text = ast.literal_eval(response.text)
        logger.info(f'LLM RESPONSE: {translated_text}')
        logger.info(f'{len(text)}--{len(translated_text)}')
        return translated_text

    def _generate_prompt(self, src_lang, tgt_lang, text):
        prompt = f'''
        Task: You are an advanced translation tool designed to deliver accurate and culturally sensitive translations. Instructions: - Translate the provided text from {src_lang} to {tgt_lang}, ensuring that the translated text is an accurate representation of the source text. - Preserve all structural elements, including special characters, spaces, line breaks, and formatting. - Respect cultural context and proper names, providing an authentic translation that considers local nuances. - Maintain the original order of sentences and special characters, refraining from adding, removing, or altering them. - Refrain from translating non-linguistic symbols and retain all tabs and spaces as they appear in the source text. - Ensure that the translated array has the same number of elements and formatting as the original, with no additions or deletions. - Finally, provide an output that is easily readable and accessible, with clear delineation between the source and target languages.
        Examples:
        Translate this text to ukrainian:\n['Report  №12_34                __Veronika Hurska__','_','     LLM USAGE IN CHATBOTS     ']
        Output:\n['Звіт  №12_34                __Вероніка Гурська__','_','    ВИКОРИСТАННЯ ВЕЛИКИХ МОВНИХ МОДЕЛЕЙ В ЧАТБОТАХ     ']
        '''

        chat_history = [
            {
                "role": "SYSTEM",
                "message": prompt
            },
            {
                "role": "USER",
                "message": f'''
                Translate this text to {tgt_lang}:\n{text}
                '''
            }
        ]
        return prompt, chat_history

