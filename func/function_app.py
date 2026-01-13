import azure.functions as func
import datetime
import json
import logging
import os
import requests
from azure.ai.translation.text import TextTranslationClient
from azure.ai.translation.document import DocumentTranslationClient
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential

region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]
resource_id = os.environ["AZURE_TEXT_TRANSLATION_RESOURCE_ID"]
endpoint = os.environ["AZURE_DOCUMENT_TRANSLATION_ENDPOINT"]

credential = DefaultAzureCredential()
transl8r = TextTranslationClient(credential=credential, region=region, resource_id=resource_id)
doctransl8r = DocumentTranslationClient(endpoint=endpoint, credential=credential)
storageclient = BlobServiceClient(
    account_url=os.environ["AZURE_STORAGE_ACCOUNT_URL"],
    credential=credential
)

app = func.FunctionApp()

@app.function_name(name="HttpTrigger1")
@app.route(route="HttpExample", auth_level=func.AuthLevel.ANONYMOUS)
def HttpExample(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    msg = "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response."
    
    if name:
        msg = f"Hello, {name}. This HTTP triggered function executed successfully."

    logging.info(msg)
    return func.HttpResponse(
            msg,
            status_code=200
    )

@app.function_name(name="SupportedLanguages")
@app.route(route="SupportedLanguages", auth_level=func.AuthLevel.ANONYMOUS)
def get_supported_languages(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Getting supported languages.')
    supported_languages = transl8r.get_supported_languages()
    return func.HttpResponse(
            json.dumps(supported_languages.as_dict()),
            status_code=200,
            mimetype="application/json"
    )

@app.function_name(name="SupportedFormats")
@app.route(route="SupportedFormats", auth_level=func.AuthLevel.ANONYMOUS)
def get_supported_formats(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Getting supported formats.')
    retval = []
    try:
        supported_formats = doctransl8r.get_supported_document_formats()
        logging.info(f"Supported formats: {supported_formats}")
        logging.info(f"Supported formats length: {len(supported_formats)}")
        for sf in supported_formats:
            retval.append({
                "content_types": sf.content_types,
                "file_extensions": sf.file_extensions,
                "file_format": sf.file_format,
                "format_versions": sf.format_versions,
                "default_format_version": sf.default_format_version

            })
    except Exception as e:
        logging.error(f"Error getting supported formats: {e}")
        return func.HttpResponse(
            f"Error getting supported formats: {str(e)}",
            status_code=500
        )
    return func.HttpResponse(
            json.dumps(retval),
            status_code=200,
            mimetype="application/json"
    )

@app.function_name(name="TranslateDocuments")
@app.route(route="TranslateDocuments", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def translate_documents(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Translating documents...')
    retval = []
    return func.HttpResponse(
            json.dumps(retval),
            status_code=200,
            mimetype="application/json"
    )

# Function to list the directories in the azure storage account under the input container
@app.function_name(name="ListDirectories")
@app.route(route="directories", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def list_directories(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Listing directories.')
    containerclient = storageclient.get_container_client("input")
    directories = []
    try:
        # List blobs in the container
        blob_list = containerclient.list_blobs()
        for blob in blob_list:
            # Check if the blob is a directory (i.e., has a trailing slash)
            if blob.name.endswith('/.ignore'):
                directories.append(blob.name[:-8])  # Remove the trailing '/.ignore' to get the directory name
    except Exception as e:
        logging.error(f"Error listing directories: {e}")
        return func.HttpResponse(
            f"Error listing directories: {str(e)}",
            status_code=500
        )

    # Logic to list directories in the Azure Storage account
    return func.HttpResponse(
            json.dumps(directories),
            status_code=200,
            mimetype="application/json"
    )

# create an azure storage account blob directory
@app.function_name(name="CreateBlobDirectory")
@app.route(route="directories", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def create_blob_directory(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Creating blob directory.')
    try:
        req_body = req.get_json()
        directory_name = req_body.get('directory_name')
        if not directory_name:
            return func.HttpResponse(
                "Please pass a directory name in the request body",
                status_code=400
            )
        
        containerclient = storageclient.get_container_client("input")
        # Create a blob with a trailing slash to represent a directory
        containerclient.upload_blob(f"{directory_name}/.ignore", data="", overwrite=True)
        
        return func.HttpResponse(
            json.dumps({ "message": f"Directory {directory_name} created successfully." }),
            status_code=201,
            mimetype="application/json"
        )
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON body",
            status_code=400
        )
    except Exception as e:
        logging.error(f"Error creating directory: {e}")
        return func.HttpResponse(
            f"Error creating directory: {str(e)}",
            status_code=500
        )

# Upload a file directly to the storage account
@app.function_name(name="UploadFile")
@app.route(route="UploadFile", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Uploading file to storage account.')
    try:
        # Get form data from the request
        directory_name = req.params.get('directory_name')
        if not directory_name:
            return func.HttpResponse(
                "Please pass a directory_name parameter",
                status_code=400
            )
        
        # Get the uploaded file from form data
        files = req.files
        if not files or 'file' not in files:
            return func.HttpResponse(
                "No file found in the request",
                status_code=400
            )
        
        uploaded_file = files['file']
        file_name = uploaded_file.filename
        file_content = uploaded_file.stream.read()
        
        if not file_name:
            return func.HttpResponse(
                "File name is required",
                status_code=400
            )
        
        # Upload the file to blob storage
        containerclient = storageclient.get_container_client("input")
        blob_name = f"{directory_name}/{file_name}"
        
        containerclient.upload_blob(
            name=blob_name,
            data=file_content,
            overwrite=True,
            content_type=uploaded_file.content_type or 'application/octet-stream'
        )
        
        return func.HttpResponse(
            json.dumps({
                "message": f"File {file_name} uploaded successfully to {directory_name}",
                "blob_name": blob_name
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return func.HttpResponse(
            f"Error uploading file: {str(e)}",
            status_code=500
        )

# Azure function to list the files in a specific directory in the input container 
@app.function_name(name="ListFilesInDirectory")
@app.route(route="directories/{directory_name:alpha}", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def list_files_in_directory(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Listing files in directory.')

    try:
        directory_name = req.route_params.get('directory_name')
        if not directory_name:
            return func.HttpResponse(
                "Please pass a directory name in the path parameter",
                status_code=400
            )

        containerclient = storageclient.get_container_client("input")
        blobs = containerclient.list_blobs(name_starts_with=f"{directory_name}/")
        files = []
        for blob in blobs:
            if not blob.name.endswith('/.ignore'):
                # Remove the directory prefix to get just the filename
                filename = blob.name[len(directory_name) + 1:]
                if filename:  # Make sure it's not empty
                    files.append(filename)

        return func.HttpResponse(
            json.dumps(files),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error listing files: {e}")
        return func.HttpResponse(
            f"Error listing files: {str(e)}",
            status_code=500
        )