import zipfile
import olefile
from xml.etree import ElementTree as ET
from io import BytesIO
from docx import Document

class DocExtractor:
    def __init__(self, file):
        self.file = file

    def extract_xml(self):
        if self.file.filename.endswith('.docx'):
            return self._extract_docx()
        elif self.file.filename.endswith('.doc'):
            return self._extract_doc()
        else:
            raise ValueError("Unsupported file type")

    def _extract_docx(self):
        with zipfile.ZipFile(self.file.file, 'r') as z:
            xml_content = z.read('word/document.xml')
            return ET.tostring(ET.fromstring(xml_content), encoding='unicode')

    def _extract_doc(self):
        ole = olefile.OleFileIO(self.file.file)
        if ole.exists('WordDocument'):
            stream = ole.openstream('WordDocument')
            doc_content = stream.read()
            return f"<xml><content>{doc_content}</content></xml>"
        else:
            raise ValueError("Unsupported DOC file format")