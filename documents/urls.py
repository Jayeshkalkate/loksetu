from django.urls import path
from . import views

urlpatterns = [

    path(
        'upload/',
        views.upload_document,
        name='upload_document'
    ),

    path(
        '',
        views.document_list,
        name='document_list'
    ),

]