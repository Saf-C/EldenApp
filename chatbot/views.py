# myproject/chatbot/views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from ML.recommend_plus import recommend_build
from ML.generate_build import generate_build, weapon_catalog
import re
import traceback


def parse_query(query: str):
    """
    Parses a user query to extract keywords for 'must_have' and 'boost'
    """
    keywords = re.findall(r'\b\w+\b', query.lower())

    # Simple logic to determine a 'must_have' and 'boost' list
    must_have = [word for word in keywords if
                 word in ['strength', 'bleed', 'dex', 'faith', 'sorcery', 'incantation', 'magic']]

    boost = {}
    # Explicit item detection with fuzzy match
    for item in weapon_catalog:
        if item.lower() in query.lower():
            must_have.append(item)
            boost[item] = boost.get(item, 0) + 5

    for word in keywords:
        if word in ['strength', 'bleed', 'dex', 'faith', 'int', 'arcane']:
            boost[word] = boost.get(word, 0) + 2  # Add a boost to these keywords
        elif word in ['greatsword', 'katana', 'armor', 'talisman', 'incantation', 'sorcery']:
            boost[word] = boost.get(word, 0) + 3  # Add a higher boost to item types

    return must_have, boost

@csrf_exempt
@require_POST
def chatbot_api(request):
    import traceback

    try:
        if request.method == "GET":
            # Quick debug mode: use query param
            query = request.GET.get("message", "")
        else:
            data = json.loads(request.body)
            query = data.get("message", "")

        must_have, boost = parse_query(query)
        recommended_builds = recommend_build(query, top_n=3, must_have=must_have, boost=boost)
        generated_build = generate_build(query=query)

        return JsonResponse({
            "status": "success",
            "results": {
                "recommended": recommended_builds,
                "generated": generated_build
            }
        })

    except Exception:
        print("=== Chatbot Exception ===")
        traceback.print_exc()
        raise