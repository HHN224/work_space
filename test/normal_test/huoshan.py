import os
from volcenginesdkarkruntime import Ark

client = Ark(
    base_url='https://ark.cn-beijing.volces.com/api/v3',
    api_key="ark-2aaf6344-3a4b-44bf-aaa7-6beacb6f4296-2060a",
)

response = client.responses.create(
    model="doubao-seed-2-0-lite-260215",
    input="hello", # Replace with your prompt
    # thinking={"type": "disabled"}, #  Manually disable deep thinking
)
print(response)