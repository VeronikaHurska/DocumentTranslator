from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from api.services.xml_processor_service import XMLProcessor

router = APIRouter()

@router.post("/translate_document", response_description="Download translated document")
async def translate_document(src_lang: str, tgt_lang: str,  output_format: str = 'docx',file: UploadFile = File(...),):
    xml_processor = XMLProcessor()
    ''' Translator API endpoint '''
    try:
        print(f"Received src_lang: {src_lang}, tgt_lang: {tgt_lang}, output_format: {output_format}")

        output_stream, media_type = xml_processor.process_and_convert(file, src_lang, tgt_lang, output_format)

        filename = f"translated_document.{output_format}"
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': media_type
        }

        return StreamingResponse(output_stream, headers=headers)
    except Exception as e:
        # Log the exception
        print(f"Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
