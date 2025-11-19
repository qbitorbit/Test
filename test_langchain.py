Quick test: LangChain with local LLM
"""
from langchain_community.llms import OpenAI

# Your local LLM connection
llm = OpenAI(
    base_url="http://10.202.1.3:8000/v1",
    api_key="dummy-key",
    model="/models/openai/gpt-oss-120b",
    temperature=0.1
)

# Test 1: Simple prompt
print("Test 1: Simple prompt")
response = llm.invoke("What is 2+2? Answer in one word.")
print(f"Response: {response}\n")

# Test 2: Longer prompt
print("Test 2: Longer prompt")
response = llm.invoke("List 3 colors. Format: 1. color, 2. color, 3. color")
print(f"Response: {response}\n")

print("✅ LangChain working with local LLM!")
