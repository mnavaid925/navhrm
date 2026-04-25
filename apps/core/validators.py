from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.deconstruct import deconstructible


IMAGE_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'webp']
DOCUMENT_EXTENSIONS = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg']

MAX_AVATAR_SIZE_MB = 5
MAX_DOCUMENT_SIZE_MB = 10
MAX_LOGO_SIZE_MB = 5

image_extension_validator = FileExtensionValidator(allowed_extensions=IMAGE_EXTENSIONS)
document_extension_validator = FileExtensionValidator(allowed_extensions=DOCUMENT_EXTENSIONS)


@deconstructible
class FileSizeValidator:
    def __init__(self, max_mb):
        self.max_mb = max_mb
        self.max_bytes = max_mb * 1024 * 1024

    def __call__(self, value):
        if value and value.size > self.max_bytes:
            raise ValidationError(
                f'File size must not exceed {self.max_mb} MB (got {value.size / 1024 / 1024:.1f} MB).'
            )

    def __eq__(self, other):
        return isinstance(other, FileSizeValidator) and self.max_mb == other.max_mb


validate_avatar_size = FileSizeValidator(MAX_AVATAR_SIZE_MB)
validate_document_size = FileSizeValidator(MAX_DOCUMENT_SIZE_MB)
validate_logo_size = FileSizeValidator(MAX_LOGO_SIZE_MB)
