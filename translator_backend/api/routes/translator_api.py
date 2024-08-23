from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from api.db.db_init import get_db
from api.services.translation_services.xml_processor_service import XMLProcessor
from api.services import ManagerS3,ManagerDB
from settings import settings
from io import BytesIO

router = APIRouter()

@router.post("/translate_document", response_description="Download translated document")
async def translate_document(
    bot_type: str,
    user_id: str,
    src_lang: str,
    tgt_lang: str,
    output_format: str = 'docx',
    file: UploadFile = File(...),
):
    xml_processor = XMLProcessor()
    s3_manager = ManagerS3(bucket_name=settings.bucket_name, user_id=user_id)
    db_manager = ManagerDB(db=get_db())
    try:
        print(f"Received src_lang: {src_lang}, tgt_lang: {tgt_lang}, output_format: {output_format}")

        # Process the file and convert it
        output_stream, media_type = xml_processor.process_and_convert(file, src_lang, tgt_lang, output_format)

        # Generate a filename
        filename = f"translated_document.{output_format}"

        # Upload the processed file to S3
        output_stream.seek(0)  # Ensure the stream is at the beginning before uploading
        file_url, s3_key = s3_manager.upload_file(output_stream, filename)

        # Get the size of the file
        file_size = s3_manager.get_file_size(output_stream)

        # Extract the translated original text
        original_text = xml_processor.extract_original_text(file)

        # Store metadata in the database
        db_manager.add_item(bot_type=bot_type, url_document=file_url, model_response=original_text, src_lang=src_lang, tgt_lang=tgt_lang)

        # Return the file as a downloadable attachment
        output_stream.seek(0)  # Ensure the stream is at the beginning before sending
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': media_type
        }

        return StreamingResponse(output_stream, media_type=media_type, headers=headers)

    except Exception as e:
        # Log the exception
        print(f"Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
