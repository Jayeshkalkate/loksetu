from django.shortcuts import render

def homepage(request):
    return render(request, 'index.html')

def aboutus(request):
    return render(request, "aboutus.html")

def services(request):
    return render(request, "services.html")

def contactus(request):
    return render(request, "contact.html")

def userprofile(request):
    return render(request, "userprofile.html")

def gallery(request):
    return render(request, "gallery.html")

def faq(request):
    return render(request, "faq.html")

def departments(request):
    return render(request, "departments.html")

def village_info(request):
    return render(request, "village_info.html")

def post(request):
    return render(request, "post.html")

def singlepost(request):
    return render(request, "singlepost.html")
