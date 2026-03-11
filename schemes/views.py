from django.shortcuts import render
from .models import Scheme
from account.models import Citizen
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Scheme

@login_required
def verify_scheme(request, scheme_id):

    scheme = get_object_or_404(Scheme, id=scheme_id)

    scheme.is_verified = True
    scheme.save()

    return redirect(request.META.get('HTTP_REFERER'))

def schemes(request):

    central = Scheme.objects.filter(
        scheme_level="central",
        is_verified=True
    )

    state = Scheme.objects.filter(
        scheme_level="state",
        state="Maharashtra",
        is_verified=True
    )

    district = Scheme.objects.none()
    taluka = Scheme.objects.none()
    village = Scheme.objects.none()

    if request.user.is_authenticated:

        citizen = Citizen.objects.filter(user=request.user).first()

        if citizen:

            district = Scheme.objects.filter(
                scheme_level="district",
                district=citizen.district,
                is_verified=True
            )

            taluka = Scheme.objects.filter(
                scheme_level="taluka",
                taluka=citizen.taluka,
                is_verified=True
            )

            village = Scheme.objects.filter(
                scheme_level="village",
                village=citizen.village,
                is_verified=True
            )

    context = {
        "central_schemes": central,
        "state_schemes": state,
        "district_schemes": district,
        "taluka_schemes": taluka,
        "village_schemes": village
    }

    return render(request, "schemes.html", context)