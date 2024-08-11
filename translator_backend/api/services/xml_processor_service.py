from lxml import etree
from io import BytesIO
import zipfile
import os
from fastapi import HTTPException
from api.services.translator_service import Translator
from api.services.llm_service import LlmTranslator
from api.settings import settings
from api.logger import logger

class XMLProcessor:
    def __init__(self):
        self.translator = LlmTranslator if settings.use_llm else Translator

    def extract_and_translate(self, xml_content, src_lang, tgt_lang):
        parser = etree.XMLParser(remove_blank_text=True)
        if isinstance(xml_content, str):
            xml_content = xml_content.encode('utf-8')
        root = etree.fromstring(xml_content, parser)
        sentences = []
        
        for elem in root.iter():
            if elem.tag.endswith('t') and elem.text and elem.text.strip():
                sentences.append(elem.text.strip())

        if settings.use_llm:
            translated_sentences = self.translator(src_lang, tgt_lang).translate(sentences)
            logger.info(f"Translated sentences LLM: {translated_sentences}")
        else:
            translated_sentences = [self.translator(src_lang, tgt_lang).translate(sentence) for sentence in sentences]
            logger.info(f"Translated sentences MODEL: {translated_sentences}")

        

        sentence_index = 0
        for elem in root.iter():
            if elem.tag.endswith('t') and elem.text and elem.text.strip():
                elem.text = translated_sentences[sentence_index]
                sentence_index += 1

        return etree.tostring(root, pretty_print=True, encoding='utf-8', xml_declaration=False)

    def convert_to_docx(self, original_file_path, translated_xml_content):
        file_stream = BytesIO()
        
        with zipfile.ZipFile(original_file_path, 'r') as original_docx:
            with zipfile.ZipFile(file_stream, 'w') as z:
                z.writestr('word/document.xml', translated_xml_content)
                
                for item in original_docx.infolist():
                    if item.filename != 'word/document.xml':
                        z.writestr(item, original_docx.read(item.filename))
        
        file_stream.seek(0)
        return file_stream

    def process_and_convert(self, file, src_lang, tgt_lang, output_format):
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(file.file.read())

        try:
            if temp_file_path.endswith('.docx'):
                xml_content = self.extract_xml_from_docx(temp_file_path)
            else:
                raise HTTPException(status_code=400, detail="Unsupported file type")

            translated_xml = self.extract_and_translate(xml_content, src_lang, tgt_lang)

            if output_format == 'docx':
                file_stream = self.convert_to_docx(temp_file_path, translated_xml)
                media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            else:
                raise HTTPException(status_code=400, detail="Unsupported output format")

            return file_stream, media_type
        finally:
            os.remove(temp_file_path)

    def extract_xml_from_docx(self, file_path):
        with zipfile.ZipFile(file_path, 'r') as docx:
            xml_content = docx.read('word/document.xml')
            return xml_content

    def get_content_types(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

    def get_rels(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''

    def get_word_rels(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>'''
