from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoProcessor, SeamlessM4TModel
from api.settings import settings

class Translator():
    def __init__(self, src_lang, tgt_lang):
        self.src_lang = src_lang
        self.tgt_lang = self.validate_language(tgt_lang)

        self.model = self.init_model()

    def validate_language(self, lang):
        if lang not in settings.helsinki_lang_codes:
            raise ValueError(f"Unsupported language: {lang}")
        return lang

    def translate(self, text):
        if self.model.startswith('facebook'):
            return self._translate_facebook(text)
        else:
            return self._translate_helsinki(text)

    def init_model(self):
        if self.src_lang == 'ukrainian' and self.tgt_lang == 'german':
            return "facebook/hf-seamless-m4t-medium"
        else:
            src_lang_code = settings.helsinki_lang_codes[self.src_lang]
            tgt_lang_code = settings.helsinki_lang_codes[self.tgt_lang]
            return f"Helsinki-NLP/opus-mt-{src_lang_code}-{tgt_lang_code}"

    def _translate_facebook(self, text):
        model_checkpoint = self.model

        processor = AutoProcessor.from_pretrained(model_checkpoint)
        model = SeamlessM4TModel.from_pretrained(model_checkpoint)

        inputs = processor(text, return_tensors="pt", padding=True)
        output_tokens = model.generate(input_ids=inputs['input_ids'],
                                       attention_mask=inputs['attention_mask'],
                                       tgt_lang='deu',
                                       generate_speech=False)
        translated_text = processor.decode(output_tokens[0].tolist()[0], skip_special_tokens=True)

        print(translated_text)
        return translated_text

    def _translate_helsinki(self, text):
        model_checkpoint = self.model
        model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
        tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        inputs = tokenizer.encode(text, return_tensors="pt", padding=True)
        outputs = model.generate(inputs)

        translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translated_text

