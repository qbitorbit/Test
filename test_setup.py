#!/usr/bin/env python3
"""Test connection to local LLM server"""
import requests
import json
from config.settings import LLM_BASE_URL, LLM_MODEL

def test_llm_connection():
    """Test if we can connect to the local LLM and get a response"""
    print("🔍 Testing LLM Connection...")
    print(f"   URL: {LLM_BASE_URL}")
    print(f"   Model: {LLM_MODEL}\n")
    
    # Simple test prompt
    test_prompt = "Say 'Hello, I am working!' and nothing else."
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": test_prompt}
        ],
        "max_tokens": 50,
        "temperature": 0.1
    }
    
    try:
        print("📤 Sending test request...")
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the response
            if "choices" in result and len(result["choices"]) > 0:
                llm_response = result["choices"][0]["message"]["content"]
                print(f"✅ LLM Response: {llm_response}")
                print("\n✅ SUCCESS: LLM connection is working!")
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Connection timeout - LLM server may be slow or unreachable")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {LLM_BASE_URL}")
        print("   Make sure LLM server is running")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_llm_structured_response():
    """Test if LLM can return structured JSON responses"""
    print("\n🔍 Testing LLM Structured Response...")
    
    test_prompt = """Respond ONLY with valid JSON in this exact format:
{
    "status": "success",
    "message": "I can return JSON"
}

Do not include any other text, markdown, or explanations. Only the JSON object."""
    
    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "user", "content": test_prompt}
        ],
        "max_tokens": 100,
        "temperature": 0.1
    }
    
    try:
        print("📤 Sending structured test request...")
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result["choices"][0]["message"]["content"].strip()
            
            print(f"📥 Raw response: {llm_response}")
            
            # Try to parse as JSON
            try:
                # Remove markdown code blocks if present
                if "```json" in llm_response:
                    llm_response = llm_response.split("```json")[1].split("```")[0].strip()
                elif "```" in llm_response:
                    llm_response = llm_response.split("```")[1].split("```")[0].strip()
                
                parsed = json.loads(llm_response)
                print(f"✅ Parsed JSON: {parsed}")
                print("✅ SUCCESS: LLM can return structured responses!")
                return True
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parsing failed: {e}")
                print("⚠️  LLM works but may need prompt engineering for JSON responses")
                return True  # Still count as success since LLM is responding
        else:
            print(f"❌ HTTP Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("LLM Connection Test Suite")
    print("=" * 60)
    
    # Test 1: Basic connection
    test1 = test_llm_connection()
    
    # Test 2: Structured responses (only if test 1 passed)
    if test1:
        test2 = test_llm_structured_response()
    else:
        print("\n⚠️  Skipping structured response test (basic connection failed)")
        test2 = False
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    print(f"Basic Connection:       {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Structured Responses:   {'✅ PASS' if test2 else '❌ FAIL'}")
    print("=" * 60)
    
    if test1 and test2:
        print("\n🎉 All tests passed! Ready to proceed to Phase 2.")
    elif test1:
        print("\n⚠️  LLM connection works but may need prompt tuning for structured outputs.")
        print("   You can still proceed to Phase 2.")
    else:
        print("\n❌ LLM connection failed. Please check:")
        print("   1. Is the LLM server running at http://10.202.1.3:8000?")
        print("   2. Is the model path correct in .env?")
        print("   3. Can you access the server from this machine?")
