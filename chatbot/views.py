from django.shortcuts import render
from django.http import JsonResponse
from ML.recommend_plus import recommend_build
from ML.generate_build import generate_build
import json


def chatbot_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.method == 'POST':
        try:
            # Handle POST request with a JSON response
            data = json.loads(request.body)
            query = data.get('query', '')

            if not query:
                return JsonResponse({'error': 'No query provided'}, status=400)

            recommended_builds = recommend_build(query, top_n=3)
            generated_build = generate_build(query=query)

            results = {
                'recommended': recommended_builds,
                'generated': generated_build,
            }
            return JsonResponse({'results': results})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Handle a standard GET request (for the initial page load)
    return render(request, 'chatbot/chatbot_page.html', {})