from enum import Enum


class MimeType(Enum):
    TXT = 'text/plain'
    PDF = 'application/pdf'
    DOC = 'application/msword'
    DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    JSON = 'application/json'
    ZIP = 'application/zip'
    JPG = 'image/jpeg'
    PNG = 'image/x-png'
