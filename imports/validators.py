import os
import zipfile

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


@deconstructible
class ZippedShapefilesValidator:
    messages = {
        'invalid_zipfile': _('%(filename)s is not a valid zip file.'),
        'mismatched_filenames': _('Files do not have a common filename prefix.'),
        'missing_required_files': _('.shp, .shx and .dbf files are required.'),
    }

    def __call__(self, value):
        if not zipfile.is_zipfile(value.file):
            raise ValidationError(
                self.messages['invalid_zipfile'],
                code='invalid_zipfile',
                params={'filename': value.file.name}
            )

        with zipfile.ZipFile(value.file) as zfile:
            required_extensions = ('.shp', '.shx', '.dbf')
            filenames, extensions = [], []
            for filename in zfile.namelist():
                if filename.endswith(required_extensions):
                    filename, extension = os.path.splitext(filename)
                    filenames.append(filename)
                    extensions.append(extension)

            if len(set(filenames)) > 1:
                raise ValidationError(
                    self.messages['mismatched_filenames'],
                    code='mismatched_filenames',
                )

            if set(extensions) != set(required_extensions):
                raise ValidationError(
                    self.messages['missing_required_files'],
                    code='missing_required_files',
                )
