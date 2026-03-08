# import os
# from openai import OpenAI

# client = OpenAI(
#     base_url="https://api.routeway.ai/v1",
#     api_key="sk-v0MYIYmHZEwYyWQv-E_xR1bgi05muj2RQrCpJnDVNEScveks-Xtn_RGqw9TgI5ozfa1cukAw6A"
# )

# response = client.chat.completions.create(
#     model="glm-4.6:free",
#     messages=[
#         {"role": "user", "content": ""}
#     ]
# )

# print(response.choices[0].message.content)



import requests

def call_glm_model(prompt, api_key):
    """
    Calls the GLM-4.6 model using Routeway.ai's free API endpoint.
    """
    url = "https://api.routeway.ai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    payload = {
        "model": "glm-4.6:free",  # Use the free-tier variant
        "messages": [
            {"role": "system", "content": "You are helpful and human-like assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3  # Lower for more deterministic coding logic
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise error for bad status codes
        
        data = response.json()
        return data['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

# Example usage:
MY_KEY = "sk-v0MYIYmHZEwYyWQv-E_xR1bgi05muj2RQrCpJnDVNEScveks-Xtn_RGqw9TgI5ozfa1cukAw6A"
result = call_glm_model("What is memory in the LLM applications and how to build it and how can we add a self-learning method in an LLM application? Tell me about it in a developer-friendly way in natural language with scenarios or examples if possible. Also how can we give more context about the user's memory to an LLM in a proper way so it could create a specialized answer the way the user wants, based on the feedback the user has given? ", MY_KEY)
print(result)
