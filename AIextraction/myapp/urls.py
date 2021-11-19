from .views import *
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('Upload_file', Upload_file, name="Upload"),
    path('Pdf_view', Pdf_view, name="Pdf_view"), 
    path('Pdf_extract', Pdf_extract, name="Pdf_extract"),
    path('Pdf_mode', Pdf_mode, name="Pdf_View"), 
    path('Adobe_pdf_extraction', Adobe_extraction, name="Adobe_extraction"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)