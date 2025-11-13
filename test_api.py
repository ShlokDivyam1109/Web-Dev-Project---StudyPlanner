#!/usr/bin/env python3
"""Quick test script to verify Gemini API connection"""

import requests
import json
import os

API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyDMcEA1fkvZ-x8AoI0HTGpKBR2pt-BXu6M')
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

print("=" * 60)
print("Testing Gemini API Connection")
print("=" * 60)

# Simple test prompt
test_prompt = """Generate a simple JSON array with 2 study schedule entries.
Return ONLY valid JSON in this format:
[
  {"subject": "Math", "topic": "Algebra", "from_date": "2025-01-01", "to_date": "2025-01-05", "normalized_weightage": 50},
  {"subject": "English", "topic": "Literature", "from_date": "2025-01-06", "to_date": "2025-01-10", "normalized_weightage": 50}
]
"""

headers = {
    'Content-Type': 'application/json',
    'X-goog-api-key': API_KEY
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": test_prompt}
            ]
        }
    ]
}

print(f"\n📝 Test Prompt: {test_prompt[:100]}...")
print(f"\n🔑 Using API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print(f"\n🌐 API URL: {API_URL}")

try:
    print("\n⏳ Sending request...")
    response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    
    print(f"✅ Request successful!")
    print(f"📊 Status Code: {response.status_code}")
    
    result = response.json()
    print(f"\n📦 Full Response:")
    print(json.dumps(result, indent=2))
    
    # Try to extract content
    if 'candidates' in result and len(result['candidates']) > 0:
        print("\n✅ Response has 'candidates'")
        candidate = result['candidates'][0]
        print(f"Candidate keys: {candidate.keys()}")
        
        if 'content' in candidate and 'parts' in candidate['content'] and len(candidate['content']['parts']) > 0:
            print("✅ Candidate has proper content/parts")
            text = candidate['content']['parts'][0].get('text', '')
            print(f"\n📝 Extracted Text ({len(text)} chars):")
            print(text)
            
            # Try to parse JSON
            import re
            # First try to extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
            if not json_match:
                # If no markdown, try direct JSON array
                json_match = re.search(r'\[[\s\S]*\]', text)
            
            if json_match:
                print("\n✅ Found JSON in response")
                try:
                    json_str = json_match.group(1) if '```' in text else json_match.group(0)
                    schedule = json.loads(json_str)
                    print(f"✅ Successfully parsed JSON: {len(schedule)} entries")
                    print(json.dumps(schedule, indent=2))
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
            else:
                print("❌ No JSON array found in response")
        else:
            print("❌ Candidate missing proper structure")
    elif 'contents' in result and len(result['contents']) > 0:
        print("\n✅ Response has 'contents' (fallback)")
        contents = result['contents'][0]
        print(f"Contents keys: {contents.keys()}")
        
        if 'parts' in contents and len(contents['parts']) > 0:
            print("✅ Contents has 'parts'")
            text = contents['parts'][0].get('text', '')
            print(f"\n📝 Extracted Text ({len(text)} chars):")
            print(text)
            
            # Try to parse JSON
            import re
            json_match = re.search(r'\[[\s\S]*\]', text)
            if json_match:
                print("\n✅ Found JSON array in response")
                try:
                    schedule = json.loads(json_match.group())
                    print(f"✅ Successfully parsed JSON: {len(schedule)} entries")
                    print(json.dumps(schedule, indent=2))
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parse error: {e}")
            else:
                print("❌ No JSON array found in response")
        else:
            print("❌ No 'parts' in contents")
    else:
        print("❌ No 'candidates' or 'contents' in response")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Request failed: {e}")
except json.JSONDecodeError as e:
    print(f"❌ Failed to parse response as JSON: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
