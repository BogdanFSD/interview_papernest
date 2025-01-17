from django.http import JsonResponse
from .models import CoverageData
from .utils import get_coordinates, wgs84_to_lambert93

def get_network_coverage(request):
    operator_mapping = {
        "20801": "Orange",
        "20810": "SFR",
        "20820": "Bouygues",
        "20815": "Free",
    }

    address = request.GET.get("q")
    if not address:
        return JsonResponse({"error": "No address provided"}, status=400)

    try:
        coordinates = get_coordinates(address)
        if not coordinates:
            return JsonResponse({"error": f"No coordinates found for address '{address}'"}, status=404)

        lon, lat = coordinates
        x, y = wgs84_to_lambert93(lon, lat)
        RADIUS = 3000

        nearby_coverage = CoverageData.objects.filter(
            x__range=(x - RADIUS, x + RADIUS),
            y__range=(y - RADIUS, y + RADIUS),
        )

        response = {}
        for coverage in nearby_coverage:
            operator_name = operator_mapping.get(coverage.operator, f"Unknown (Code={coverage.operator})")
            response[operator_name] = {
                "2G": coverage.g2,
                "3G": coverage.g3,
                "4G": coverage.g4,
            }

        if not response:
            return JsonResponse({"error": "No coverage data found for the given location"}, status=404)

        return JsonResponse(response)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=400)
