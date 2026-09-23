from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),
    path('', views.document_list, name='document_list'),
    path('<int:document_id>/', views.document_detail, name='document_detail'),
    path('<int:document_id>/download/', views.download_document, name='download_document'),
    path('<int:document_id>/delete/', views.delete_document, name='delete_document'),
]