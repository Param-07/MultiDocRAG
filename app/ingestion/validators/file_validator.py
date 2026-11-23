
from pathlib import Path
import codecs
from fastapi import UploadFile

from ..exceptions import FileValidationError


ALLOWED_FILE_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".md": "text/markdown",
}


def validate_uploaded_file(file: UploadFile) -> None:
    """
    Validate the uploaded file's filename extension and MIME type.

    Raises:
        ValueError: If the filename, extension, or MIME type is invalid.
    """

    # 1. Validate filename
    if not file.filename:
        raise FileValidationError(
            message="File name is missing",
            code="NO_FILE_NAME",
            status_code=400
        )

    # 2. Extract extension (case-insensitive)
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_FILE_TYPES:
        raise FileValidationError(
            message=f"Unsupported file type. Expected {list(ALLOWED_FILE_TYPES.keys())}, but received '{extension}'.",
            code="UNSUPPORTED_FILE_TYPE",
            status_code=415
        )

    # 3. Get expected MIME type for the extension
    expected_mime_type = ALLOWED_FILE_TYPES[extension]

    # 4. Validate MIME type
    if file.content_type != expected_mime_type:
        raise FileValidationError(
            message= f"""MIME type mismatch. Expected '{expected_mime_type}', "
            f"but received '{file.content_type}'.""",
            code="INVALID_MIME_TYPE",
            status_code=415
        )

    # 5. Validate file size (if available)
    if file.size is None:
        raise FileValidationError(
            message="Unable to determine file size",
            code="SIZE_ERROR",
            status_code=400

        )

    # 6. Check if the file is empty or exceeds the maximum allowed size
    if file.size == 0:
        raise FileValidationError(
            message="File is empty",
            code="EMPTY_FILE",
            status_code=400
        )

    MAX_FILE_SIZE = 50 * 1024 * 1024
    if file.size > MAX_FILE_SIZE:
        raise FileValidationError(
            message="File size exceeds the maximum allowed limit of 50 MiB.",
            code="FILE_TOO_LARGE",
            status_code=413
        )
    
    # 7. Validate file signature (magic number) based on the extension
    if validate_file_signature(file, extension) is False:
        raise FileValidationError(
            message="File signature does not match the expected format for the given extension.",
            code="INVALID_FILE_ENCODING",
            status_code=422
        )




import zipfile
import xml.etree.ElementTree as ET

from pathlib import PurePosixPath


OFFICE_PACKAGE_REQUIREMENTS = {
    ".docx": {
        "main_part": "word/document.xml",
        "content_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
    },
    ".pptx": {
        "main_part": "ppt/presentation.xml",
        "content_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml",
    },
    ".xlsx": {
        "main_part": "xl/workbook.xml",
        "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml",
    },
}

MAX_ZIP_ENTRIES = 10_000
MAX_UNCOMPRESSED_SIZE = 200 * 1024 * 1024


def validate_office_package(file: UploadFile) -> None:
    """
    Validate the internal structure of DOCX, PPTX and XLSX files.
    Does not extract files to disk.
    """

    if not file.filename:
        raise FileValidationError(
            message="Filename is missing.",
            code="INVALID_FILENAME",
            status_code=400
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in OFFICE_PACKAGE_REQUIREMENTS:
        return

    requirements = OFFICE_PACKAGE_REQUIREMENTS[extension]

    try:
        file.file.seek(0)

        with zipfile.ZipFile(file.file, "r") as archive:

            entries = archive.infolist()

            # Check number of archive entries
            if len(entries) > MAX_ZIP_ENTRIES:
                raise FileValidationError(
                    message="Office archive contains too many entries.",
                    code="INVALID_ARCHIVE_ENTRIES",
                    status_code=422
                )

            # Check total uncompressed size
            total_size = sum(entry.file_size for entry in entries)

            if total_size > MAX_UNCOMPRESSED_SIZE:
                raise FileValidationError(
                    message="Office archive exceeds the allowed uncompressed size.",
                    code="INVALID_UNCOMPRESSED_SIZE",
                    status_code=422
                )

            # Reject suspicious archive paths
            for entry in entries:
                path = PurePosixPath(entry.filename)

                if path.is_absolute() or ".." in path.parts:
                    raise FileValidationError(
                        message="Office archive contains an unsafe path.",
                        code="INVALID_ARCHIVE_PATH",
                        status_code=422
                    )

                # Reject encrypted entries
                if entry.flag_bits & 0x1:
                    raise FileValidationError(
                        message="Encrypted Office archives are not supported.",
                        code="INVALID_ENCRYPTION",
                        status_code=422
                    )

            # Required package files
            required_files = {
                "[Content_Types].xml",
                "_rels/.rels",
                requirements["main_part"],
            }

            archive_files = set(archive.namelist())

            if not required_files.issubset(archive_files):
                raise FileValidationError(
                    message="Invalid Office document structure.",
                    code="INVALID_DOCUMENT_STRUCTURE",
                    status_code=422
                )

            # Validate content types XML
            content_types_data = archive.read("[Content_Types].xml")
            root = ET.fromstring(content_types_data)

            expected_content_type = requirements["content_type"]
            expected_part = "/" + requirements["main_part"]

            matching_override = any(
                element.attrib.get("PartName") == expected_part
                and element.attrib.get("ContentType") == expected_content_type
                for element in root
                if element.tag.endswith("Override")
            )

            if not matching_override:
                raise FileValidationError(
                    message="Office document format does not match its extension.",
                    code="INVALID_DOCUMENT_FORMAT",
                    status_code=422
                )

            # Validate the main document XML
            main_document = archive.read(requirements["main_part"])
            ET.fromstring(main_document)

    except (zipfile.BadZipFile, zipfile.LargeZipFile, ET.ParseError, KeyError, OSError):
        raise FileValidationError(
            message="The uploaded Office document is corrupted.",
            code="INVALID_DOCUMENT",
            status_code=422
        )

    finally:
        file.file.seek(0)

def validate_file_signature(file: UploadFile, extension: str) -> bool:
    """
    Validate the file signature (magic number) based on the file extension.

    Args:
        file (UploadFile): The uploaded file.
        extension (str): The file extension.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    # Read the first few bytes of the file to check its signature
    signature = file.file.read(8)
    file.file.seek(0)  # Reset the file pointer after reading

    if extension == ".pdf":
        return signature.startswith(b"%PDF")
    elif extension == ".txt":
        return validate_file_encoding(file) is None  # No specific signature for text files
    elif extension == ".docx":
        return validate_office_package(file) is None  # DOCX files are ZIP archives
    elif extension == ".pptx":
        return validate_office_package(file) is None  # PPTX files are ZIP archives
    elif extension == ".xlsx":
        return validate_office_package(file) is None  # XLSX files are ZIP archives
    elif extension == ".md":
        return validate_file_encoding(file) is None  # No specific signature for markdown files

    return False

def validate_file_encoding(file: UploadFile) -> None:
    """
    Validate the encoding of text files (TXT and MD).

    Raises:
        ValueError: If the file encoding is not UTF-8.
    """
    extension = Path(file.filename).suffix.lower()
    decoder = codecs.getincrementaldecoder("utf-8-sig")()

    if extension in {".txt", ".md"}:
        try:
            # Read a small portion of the file to check encoding
            while True:
                chunk = file.file.read(8192)  # Read in chunks of 8192 bytes
                if not chunk:
                    break
                decoder.decode(chunk)

            decoder.decode(b"", final=True)  # Finalize the decoding
        except UnicodeDecodeError:
            raise FileValidationError(
                message="Text files must be encoded in UTF-8.",
                code="INVALID_ENCODING",
                status_code=422
            )
        finally:
            file.file.seek(0)  # Reset the file pointer after reading

