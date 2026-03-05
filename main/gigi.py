import os
from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("API_BASE"),
    api_key=os.getenv("API_KEY"),
)

print("----- standard request -----")
completion = client.chat.completions.create(
    model="doubao-1-5-lite-32k-250115",
    messages=[
        {"role": "user", "content": "hello I'm gigi."},
    ],
)
print(completion.choices[0].message.content)

print("----- streaming request -----")
stream = client.chat.completions.create(
    model="doubao-1-5-lite-32k-250115",
    messages=[
        {"role": "system", "content": "You are kiki."},
        {"role": "user", "content": "hello I'm gigi."},
    ],
    stream=True,
)
for chunk in stream:
    if not chunk.choices:
        continue
    print(chunk.choices[0].delta.content, end="")
print()

