from django.shortcuts import render, redirect
from .forms import DocumentForm
from .models import Document
from django.contrib.auth.decorators import login_required


@login_required
def upload_document(request):

    if request.method == "POST":

        form = DocumentForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            doc = form.save(commit=False)

            doc.uploaded_by = request.user

            doc.save()

            return redirect(
                'document_list'
            )

    else:

        form = DocumentForm()

    return render(
        request,
        'documents/upload.html',
        {'form': form}
    )


@login_required
def document_list(request):

    documents = Document.objects.all()

    context = {
        "documents": documents
    }

    return render(
        request,
        "list.html",
        context
    )