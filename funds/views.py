from django.shortcuts import render

from .models import Fund


def fund_list(request):
    year = request.GET.get('year', '').strip()
    funds = Fund.objects.select_related('department').all()
    if year:
        funds = funds.filter(financial_year=year)
    years = list(Fund.objects.order_by('-financial_year').values_list('financial_year', flat=True).distinct())
    return render(request, 'funds/list.html', {
        'title': 'Government Funds',
        'funds': funds,
        'year': year,
        'years': years,
        'total': funds.count(),
    })
