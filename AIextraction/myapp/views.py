from django.http.response import HttpResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse, Http404
import os 
import PyPDF2
import pandas as pd 
import csv
import numpy as np
import logging
import os.path
import zipfile

from adobe.pdfservices.operation.auth.credentials import Credentials
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_pdf_options import ExtractPDFOptions
from adobe.pdfservices.operation.pdfops.options.extractpdf.extract_element_type import ExtractElementType
from adobe.pdfservices.operation.execution_context import ExecutionContext
from adobe.pdfservices.operation.io.file_ref import FileRef
from adobe.pdfservices.operation.pdfops.extract_pdf_operation import ExtractPDFOperation

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# function to upload any file 
def Upload_file(request):
    if request.method == 'POST': 
        request_file = request.FILES['document'] if 'document' in request.FILES else None

        if request_file:
                    fs = FileSystemStorage()
                    file = fs.save(request_file.name, request_file)
                    fileurl = fs.url(file)
                    # print(fileurl)
    
    return render(request, "myapp/upload_file.html")

# function to view the uploaded file 
def Pdf_view(request):
    try:
        filepath = os.path.join('media', 'Anantara–JOURNEYS-ED1.pdf')
        return FileResponse(open(filepath, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()

def Pdf_extract(request):
    try:
        filepath = os.path.join('media', 'Anantara–JOURNEYS-ED1.pdf')
        pdfFileObject = open(filepath, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObject)
        # print(pdfFileObject)
        no_of_pages = pdfReader.numPages
        df1 = pd.DataFrame()
        for i in range(0,no_of_pages):
            try:
                pageObject = pdfReader.getPage(i)
                page_data = pageObject.extractText()
                page_details = page_data.split('\n')
                page_dict = {"header":page_details[0], "title":page_details[1], "body":page_details[2:], "Page_No": i+1}

            except Exception as ex:
                page_dict = {"header":[""], "title":[""], "body":[""], "Page_No": i}

            # page_data = pageObject.extractText()
            # page_details = page_data.split('\n')
            # page_dict = {"header":page_details[0], "title":page_details[1], "body":page_details[2:], "Page_No": i}
            # page_details.append(i)
            # print('out')
            df = pd.DataFrame.from_dict(page_dict)
            # pages = pages + page_details
            # print(pages)
            df1 = df1.append(df, ignore_index=True)
            df1 = df1.replace('', np.nan)
            df1.dropna(inplace=True)
        # df1 = pd.DataFrame(pages, index=None)    
        # print(df1)  
        pdfFileObject.close()
        return HttpResponse(df1.to_html())
                    
    except Exception as ex:
        print(ex)


def Pdf_mode(request):
    return render(request, "myapp/pdf_view.html")

def Adobe_extraction(request):
    try:
        # get base path.
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Initial setup, create credentials instance.
        credentials = Credentials.service_account_credentials_builder() \
            .from_file(base_path + "/AIextraction/pdfservices-api-credentials.json") \
            .build()

        # Create an ExecutionContext using credentials and create a new operation instance.
        execution_context = ExecutionContext.create(credentials)
        extract_pdf_operation = ExtractPDFOperation.create_new()

        # Set operation input from a source file.
        source = FileRef.create_from_local_file(base_path + "/AIextraction/media/extractPdfInput.pdf")

        extract_pdf_operation.set_input(source)

        # Build ExtractPDF options and set them into the operation
        extract_pdf_options: ExtractPDFOptions = ExtractPDFOptions.builder() \
            .with_element_to_extract(ExtractElementType.TEXT) \
            .build()
        extract_pdf_operation.set_options(extract_pdf_options)

        # Execute the operation.
        result: FileRef = extract_pdf_operation.execute(execution_context)

        # Save the result to the specified location.
        result.save_as(base_path + "/output/ExtractTextInfoFromPDF.zip")
        file_to_extract = "structuredData.json"

        # extract the json
        with zipfile.ZipFile(base_path + "/output/ExtractTextInfoFromPDF.zip") as z:
            with open(file_to_extract, 'wb') as f:
                f.write(z.read(file_to_extract))
                print("PDF Extracted", file_to_extract) 
                os.remove(base_path + "/output/ExtractTextInfoFromPDF.zip")
        fle = open("/Users/achal/Documents/Versoview-AI/AIextraction/" + file_to_extract)
        print(fle)
        return HttpResponse(fle)

    except (ServiceApiException, ServiceUsageException, SdkException):
         logging.exception("Exception encountered while executing operation")

