from os.path import join, exists
import pydicom, pydicom.misc


def validateDicomFile(upload_dir,study, filename):
    file_path = join(upload_dir, study, filename)
    if not exists(file_path) or file_path.endswith(".tmp"):
        raise ValueError("file not found")

    if not pydicom.misc.is_dicom(file_path):
        return ValueError("not a valid DICOM file")

    return pydicom.dcmread(file_path)


def errorResponse(error):
    return {
        "success": False,
        "error": error
    }


def errorResponseWithParams(params):
    return {
        "success": False,
        **params
    }


def successResponse(params):
    return {
        "success": True,
        **params
    }

