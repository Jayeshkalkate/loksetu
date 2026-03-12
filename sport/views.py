from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Tournament


def sport_events(request):

    # Citizens only see verified tournaments
    if request.user.is_authenticated:

        role = request.user.userprofile.role

        if role in ["super_admin", "state_admin"]:
            tournaments = Tournament.objects.all().order_by("-start_date")
        else:
            tournaments = Tournament.objects.filter(is_verified=True).order_by("-start_date")

    else:
        tournaments = Tournament.objects.filter(is_verified=True).order_by("-start_date")

    return render(request, "events.html", {
        "tournaments": tournaments
    })


@login_required
def verify_tournament(request, id):

    tournament = get_object_or_404(Tournament, id=id)

    role = request.user.userprofile.role

    if role in ["super_admin", "state_admin"]:
        tournament.is_verified = True
        tournament.save()

    return redirect("sport_events")

@login_required
def add_tournament(request):

    if request.user.userprofile.role not in ["super_admin","state_admin"]:
        return redirect("/")

    if request.method == "POST":

        Tournament.objects.create(
            title=request.POST["title"],
            village=request.POST["village"],
            district=request.POST["district"],
            start_date=request.POST["start_date"],
            end_date=request.POST["end_date"],
            cricheroes_link=request.POST["cricheroes_link"],
        )

        return redirect("sport_events")

    return render(request,"add_tournament.html")