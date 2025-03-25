import azure.functions as func
import datetime
import json
import logging
import os
import requests
from azure.ai.translation.text import TextTranslationClient
from azure.identity import DefaultAzureCredential

region = os.environ["AZURE_TEXT_TRANSLATION_REGION"]
resource_id = os.environ["AZURE_TEXT_TRANSLATION_RESOURCE_ID"]

credential = DefaultAzureCredential()
transl8r = TextTranslationClient(credential=credential, region=region, resource_id=resource_id)

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

# @app.blob_trigger(arg_name="myblob", source="EventGrid", path="temp",
#                            connection="AzureWebJobsStorage") 
# def EventGridBlobTrigger(myblob: func.InputStream):
#     logging.info(f"Python blob trigger function processed blob"
#             f"Name: {myblob.name}"
#             f"Blob Size: {myblob.length} bytes")
#     requests.get(f'https://{os.environ["WEBSITE_DEFAULT_HOSTNAME"]}/www/httpexample?name={myblob.name}')