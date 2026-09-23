import logging
import mimetypes
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import DocumentForm
from .models import Document

logger = logging.getLogger(__name__)


@login_required
def upload_document(request):
    """Upload a new document."""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, _('Document uploaded successfully.'))
            return redirect('documents:document_list')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = DocumentForm()

    return render(request, 'documents/upload.html', {'form': form})


@login_required
def document_list(request):
    """List all documents the user can access."""
    # Users can see their own documents and public ones.
    # Staff/super_admin see all.
    if request.user.is_staff or request.user.has_perm('documents.can_delete_any_document'):
        docs = Document.objects.all()
    else:
        docs = Document.objects.filter(is_public=True) | Document.objects.filter(uploaded_by=request.user)
    docs = docs.distinct().order_by('-uploaded_at')

    paginator = Paginator(docs, 20)
    page = request.GET.get('page')
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)

    return render(request, 'documents/list.html', {'documents': documents})


@login_required
def document_detail(request, document_id):
    """View document details and allow download."""
    doc = get_object_or_404(Document, id=document_id)
    # Check access: public, owner, or staff
    if not (doc.is_public or doc.uploaded_by == request.user or request.user.is_staff):
        messages.error(request, _('You do not have permission to view this document.'))
        return redirect('documents:document_list')
    return render(request, 'documents/detail.html', {'document': doc})


@login_required
def download_document(request, document_id):
    """Download the actual file."""
    doc = get_object_or_404(Document, id=document_id)
    # Check access
    if not (doc.is_public or doc.uploaded_by == request.user or request.user.is_staff):
        messages.error(request, _('You do not have permission to download this document.'))
        return redirect('documents:document_list')

    if not doc.file:
        raise Http404('File not found.')

    # Try to guess content type
    content_type, encoding = mimetypes.guess_type(doc.file.name)
    if not content_type:
        content_type = 'application/octet-stream'

    response = FileResponse(doc.file, content_type=content_type)
    # Set Content-Disposition to inline or attachment
    filename = quote(doc.file.name.split('/')[-1])
    response['Content-Disposition'] = f'inline; filename*=UTF-8\'\'{filename}'
    return response


@login_required
@permission_required('documents.can_delete_any_document', raise_exception=True)
def delete_document(request, document_id):
    """Delete a document (staff/super_admin only)."""
    doc = get_object_or_404(Document, id=document_id)
    if request.method == 'POST':
        doc.file.delete(save=False)  # delete physical file
        doc.delete()
        messages.success(request, _('Document deleted successfully.'))
        return redirect('documents:document_list')
    return render(request, 'documents/confirm_delete.html', {'document': doc})