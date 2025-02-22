import os
from os import listdir, mkdir, unlink
from os.path import isfile, join, isdir, exists, dirname
import pydicom, pydicom.misc
from flask import Flask, flash, request, redirect, url_for, send_file

from src.convert import mri_to_png
from src.util import successResponse, errorResponseWithParams, errorResponse, validateDicomFile

app = Flask(__name__)
APP_DIR = dirname(dirname(__file__))
UPLOAD_DIR = APP_DIR + '/files/dicom'
PNG_DIR = APP_DIR + '/files/png'

print(APP_DIR)


"""
This endpoints allows the user to upload DICOM files and store it under a specific study name
The study name should be xray, 
For example: iraj-2025-xray
"""
# upload file
@app.route("/", methods=['GET'])
def upload_form():
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data action=/upload>
      <label for="study">Study:</label>
      <input type=text name=study multiple><br/>
      <label for="files">Files:</label>
      <input type=file name=files multiple>
      <input type=submit value=Upload>
    </form>
    '''


"""
The root level of files are categorized using Study.
"""
@app.route("/files")
def get_studies():
    directories = [f for f in listdir(UPLOAD_DIR) if isdir(join(UPLOAD_DIR, f))]
    return successResponse({
        "studiesCount": len(directories),
        "studies": directories
    })


"""
This endpoints will return of files that are stored under a single study
"""
@app.route("/files/<study>")
def get_files(study):
    files = []
    for file in listdir(join(UPLOAD_DIR, study)):
        file_path = join(UPLOAD_DIR, study, file)
        if isfile(file_path) and not file_path.endswith(".tmp"):
            files.append(file)

    return successResponse({
        "study": study,
        "filesCount": len(files),
        "files": files
    })


"""
This will accept multiple files for a single study. 
"""
@app.route("/upload", methods=['POST'])
def upload_file():
    study = request.form.get('study')
    files = request.files.getlist('files')

    if not study or len(files) == 0:
        return {"error": "either study or files parameter is missing"}

    # check for study folder and create one it doesn't exists
    dir_path = join(UPLOAD_DIR, study)
    if not isdir(dir_path):
        mkdir(dir_path)

    # check for files and format before storing them
    failed_files = []
    for file in files:
        # save the file temporarily to validate its content
        # if any file fails validate we will reject all files
        # this can be improved to avoid saving the file unnessarilly
        tmp_file_path = join(dir_path, file.filename + ".tmp")
        file.save(tmp_file_path)
        if not pydicom.misc.is_dicom(tmp_file_path):
            failed_files.append({
                "name": file.filename,
                "reason": "invalid_type"
            })

        # check if file already exists
        final_file_path = join(dir_path, file.filename)
        if exists(final_file_path):
            failed_files.append({
                "name": file.filename,
                "reason": "duplicate"
            })

    if failed_files:
        return errorResponseWithParams({
            "failedFiles": len(failed_files),
            "files": failed_files
        })

    # files are valid and can be processed as permanent
    result = []
    for file in files:
        tmp_file_path = join(dir_path, file.filename + ".tmp")
        final_file_path = join(dir_path, file.filename)
        os.rename(tmp_file_path, final_file_path)
        result.append({
            "name": file.filename,
            "size": file.content_length,
            "mime": file.mimetype
        })

    # return list of files uploaded
    return successResponse({
        "filesUploaded": len(files),
        "files": result
    })

"""
This endpoints return the tags details from the Dicom file.
User can provide an array of tag=(0000,0000) format.
"""
@app.route("/files/<study>/<filename>/tag", methods=['GET'])
def get_file_tags(study, filename):
    input_tags = request.args.getlist('tag')
    # check if tag is empty
    if not input_tags:
        return errorResponse("tag query parameter is empty")

    try:
        plan = validateDicomFile(UPLOAD_DIR, study, filename)
    except ValueError as e:
        return errorResponse(e.args[0])

    # validate the format of all tags
    invalid_tags = []
    result = []
    for tag in input_tags:
        [part_one, part_two] = tag.replace('(', '').replace(')', '').split(',')
        # check if part one and part two are parsed and are not empty
        if not part_one or not part_two:
            invalid_tags.append(tag)
            continue

        tag_tuple = (part_one, part_two)
        try:
            element = plan[tag_tuple]
        except:
            invalid_tags.append(tag)
            continue

        result.append({
            "value": element.value,
            "name": element.name,
            "keyword": element.keyword,
            "tag": tag,
            "VM": element.VM,
            "VR": element.VR,
        })

    if len(invalid_tags):
        return errorResponseWithParams({
            "invalidTags": invalid_tags
        })

    return successResponse({
        "study": study,
        "file": filename,
        "tags": result
    })


"""
This endpoint will generate the PNG file for a specific DICOM file 
and stored in the filesystem.
"""
@app.route("/files/<study>/<filename>/png", methods=['GET'])
def get_file_png(study, filename):
    # if png file is already generated then sent the existing one
    png_file_path = join(PNG_DIR, study, filename + '.png')
    if exists(png_file_path):
        return send_file(png_file_path, mimetype='image/png')

    #validate the dicom file
    try:
        plan = validateDicomFile(UPLOAD_DIR, study, filename)
    except ValueError as e:
        return errorResponse(e.args[0])

    # create new directory to store the png file if it doesn't exists
    png_file_dir = join(PNG_DIR, study)
    if not isdir(png_file_dir):
        mkdir(png_file_dir)

    png_file = open(png_file_path, 'wb')
    # try:
    mri_to_png(plan, png_file)
    png_file.close()
    # except:
    #     png_file.close()
    #     unlink(png_file_path)
    #     return errorResponse("Unable to convert DICOM to png")

    return send_file(png_file_path, mimetype='image/png')
