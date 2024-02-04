from openai import OpenAI
API_KEY = "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"
client = OpenAI(api_key = API_KEY)

def askGPT(prompt) -> str:
  completion = client.chat.completions.create(
  model="gpt-4-turbo-preview",
  messages=[
    {"role": "user", "content": prompt}
  ]
  )
  result = completion.choices[0].message.content
  print(result)
  return result