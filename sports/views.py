
from django.http import JsonResponse


def players_list(request):
    return JsonResponse([], safe=False)
