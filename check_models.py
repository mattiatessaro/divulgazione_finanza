from openai import OpenAI

client = OpenAI(api_key="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")

models = client.models.list()

for model in models.data:
    print(model.id)
