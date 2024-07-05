from groq import Groq
import os

os.environ['GROQ_API_KEY'] = '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'

content = 'summary of'
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "user",
            "content": content,
        },
       
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=True,
    stop=None,
)

with open("output.txt", "w") as f:
    for chunk in completion:
        output = chunk.choices[0].delta.content or ""
        f.write(output)