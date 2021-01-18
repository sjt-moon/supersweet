import os
import pandas as pd
from .logger import Logger

EXCEL_ENGINE = 'openpyxl'


def read_file(temporary_uploaded_file, **kwargs):
    """Read file with **kwargs. Files supported: xls, xlsx, csv, csv.gz, pkl. This will read from the temporary file.

    Input: filename stored in Django. Type: django.core.files.uploadedfile.TemporaryUploadedFile.
           First a file is uploaded. In settings.py FILE_UPLOAD_HANDLERS sets this to always make a copy to the
           temporary storage. If FILE_UPLOAD_HANDLERS is not set, then it would use in-memory files for those < 2.5M.
           The front-end HTML can embed the uploaded filename, and then the views.py can read it from
           request.FILES[upload file name]. Then get its temporary copy, and open it into DataFrame.
    Return: data frame
    """
    read_map = {'xls': pd.read_excel, 'xlsx': pd.read_excel, 'csv': pd.read_csv,
                'gz': pd.read_csv, 'pkl': pd.read_pickle}
    filename = temporary_uploaded_file.temporary_file_path()
    ext = os.path.splitext(filename)[1].lower()[1:]

    assert ext in read_map, "Input file not in correct format, must be {0}; current format is '{1}'".format(
        read_map.keys(), ext)
    assert os.path.isfile(filename), "File Not Found Exception '{0}'.".format(filename)
    Logger.info("read file %s (local copy %s)" % (temporary_uploaded_file.name, filename))

    kwargs['engine'] = EXCEL_ENGINE
    return read_map[ext](filename, **kwargs)
