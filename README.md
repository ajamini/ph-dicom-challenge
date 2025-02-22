#DICOM Microservice
A minimal Flask-based microservice for handling DICOM files. The service can:

1. Accept and store DICOM files (upload).
2. Extract and return specific DICOM header attributes based on query parameters.
3. Convert DICOM files to PNG images for easier viewing in browsers.

## Overview
This microservice serves as an entry point to a DICOM management system. It currently allows:

- File uploads (grouped by a study name).
- Basic extraction of DICOM header information (e.g., Patient Name, Study Date).
- Generation of a PNG image from a DICOM file for front-end viewing.

The main objective is to demonstrate how a simple RESTful service can be set up in Python/Flask to handle DICOM files. The next step is to integrate a database (e.g., MySQL) for storing DICOM metadata and to allow for advanced querying and retrieval of DICOM files.

Resource Used:

1. https://www.dicomlibrary.com/dicom/dicom-tags/
2. https://dicom.innolitics.com/ciods/
3. https://pmc.ncbi.nlm.nih.gov/articles/PMC3354356
3. https://dicomiseasy.blogspot.com/2012/08/chapter-12-pixel-data.html

## Installation and Setup

1. Clone the repository:
```
git clone https://github.com/your-repo/dicom-microservice.git
cd dicom-microservice
```

2. Create a virtual environment (optional, but recommended):
```
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

3. Install the dependencies:
```
pip install -r requirements.txt
```

4. Run the Flask server:
```
FLASK_APP=src/index.py python -m flask run 
```

By default, Flask will run on http://127.0.0.1:5000.

> Note: Ensure that you have a valid version of Python (3.7+) installed, as many DICOM libraries (such as pydicom) require Python 3.7 or above.

## Documents
All documents are stored in the local filesystem, and they are organized using Study name that user provided they are uploaded single or multiple files.

There are 2 endpoints that you can use to find the right document. First endpoints shows all the different Study folders, and the second endpoints shows all the files stored inside that folder.

No database was utilized for this project to keep it simple. Read the section about future improvement on how we can integrate database.


## API Endpoints
Below are the endpoints available in the current version of this microservice:

### Form (for uploading)
GET /

Include a simple form that will allow you make a POST call to the upload endpoints. In this form you can type in the Study name and attach single or multiple files at once.

### POST /upload
Uploading DICOM files to server to validate and store.

Allows you to upload a DICOM file along with a study name that categorizes the uploaded file.

This endpoint takes an array of files and a study parameter. It will create a folder in the filesystem using the study parameter and store all the files in it.

Files are stored as temporary files first, allowing us to validate their content against the DICOM format.

#### Request
Body: multipart/form-data with key file containing the DICOM file.
```
study=iraj-x-ray&files=...&files=..&files=...
```

#### Error
Only DICOM file are permitted regardless of their file extension. 
```
{
  "failedFiles": 1,
  "files": [
    {
      "name": "sample.pdf",
      "reason": "invalid_type"
    }
  ],
  "success": false
}
```

If duplicate filename existing in under the study, you will get an error.
```
{
  "failedFiles": 1,
  "files": [
    {
      "name": "IM000001",
      "reason": "duplicate"
    }
  ],
  "success": false
}
```

### Get list of all Studies
GET /files
```
{
  "studies": [
    "iraj-x-ray"
  ],
  "studiesCount": 1,
  "success": true
}
```


### Get list of files in a study folder
GET /files/iraj-x-ray
```
{
  "files": [
    "IM000001",
    "IM000020"
  ],
  "filesCount": 2,
  "study": "iraj-x-ray",
  "success": true
}
```

### GET files/:study/:file/tag?tag=:tag
Reads a DICOM file in the specified study folder, extracts the value of the specified DICOM tags, and returns it.

#### Request
Parameter: `tag`, the DICOM tag you want to retrieve (e.g., tag=(0028,0012)&tag=(0028,0011)).

```
{
  "file": "IM000001",
  "study": "Test",
  "success": true,
  "tags": [
    {
      "VM": 1,
      "VR": "US",
      "keyword": "Columns",
      "name": "Columns",
      "tag": "(0028,0011)",
      "value": 967
    },
    {
      "VM": 1,
      "VR": "US",
      "keyword": "Rows",
      "name": "Rows",
      "tag": "(0028,0010)",
      "value": 1053
    }
  ]
}
```

#### Error
Incorrect file name
```
{
  "error": "file not found",
  "success": false
}
```


Missing tag param in the query
```{
  "error": "tag query parameter is empty",
  "success": false
}
```


Invalid tag
```
{
  "invalidTags": [
    "(2222,2222)"
  ],
  "success": false
}
```

### GET files/:study/:file/png
Converts the specified DICOM file to a PNG image and returns it as a binary stream (image).
```
Return a PNG IMAGE
```

#### Error
Incorrect file name
```
{
  "error": "file not found",
  "success": false
}
```


## Future Improvements
Below are suggestions on how this project can be made more robust and scalable:

### Database 
We didn't utilize any database for the current project. Utilizing a database to parse file attributes and store them would allow for easy search functionality. Users could quickly and easily search for files by PatientID or PatientName.

When files are uploaded, we wouldn't need to ask for any study details. The process could automatically extract all essential information from each file. This also allows for better document storage options since we no longer need to organize files into folders for quick access.

### Storage
Using an external cloud storage service like S3 or Azure File Storage to store all the files allows us to leverage security and versioning features to create a robust file storage system.

Without the need to organize the files into folders, we can generate a random name for each file and store them in a flat list.

### Worker
We should use a queue system to process all files through workers that can perform memory- and CPU-intensive operations, such as extracting details, analyzing attributes, generating browser-compatible images (PNG, JPEG, GIF), creating GIF of all images and handling image processing for machine learning purposes.

### Security
Implement authentication via JSON Web Tokens (JWT) or OAuth2 to restrict access to the endpoints. We should create different roles like admin, standard users, and read-only users.

### Testing
Implement a robust test suite (e.g., using pytest or unittest) to cover unit tests, integration tests, and edge cases. 

Automate the testing process with a Continuous Integration (CI) pipeline, such as GitHub Actions or Jenkins, to ensure consistent quality and reliability with every new commit or pull request.

### Other Enhancements
Better logging and application performance monitoring (e.g., New Relic) can provide real-time insight into system health and performance.

Perform robust validation to ensure uploaded files are truly DICOM and handle invalid or corrupted files more gracefully.

Add endpoints that allow searching by patient name, institution, date range, and modality.

Create a Dockerfile for containerizing the microservice to ensure consistent environments.

Use third-party error tracking (e.g., Sentry) for quick diagnosis of issues in production.

## License
This project is licensed under the Apache License. You are free to modify and distribute this project, but please provide credit to the original authors.

## Credit
We appreciate and thank the maintainers of the following repo for making their work available.
- https://github.com/dennyglee/dicom-to-png
