import os
import requests

url = "https://api.x.ai/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}"
}
payload = {
    "messages": [
        {
            "role": "user",
            "content": "What is the current leading theory as to what downed the Air India Dreamliner recently?"
        }
    ],
    "search_parameters": {
        "mode": "on",
        "return_citations": True,
        "from_date": "2025-06-01",
        "to_date": "2025-06-28",
        "max_search_results": 10,
        "sources": [
            {
                "type": "web",
                "excluded_websites": [
                    "wikipedia.org",
                    "reddit.com"
                ],
                "allowed_websites": [
                    "space.com"
                ],
                "safe_search": False
            }
        ]
    },
    "model": "grok-3-latest"
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
