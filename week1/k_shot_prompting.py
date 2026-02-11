import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
When I write reverse (XXXXX), the XXXXX will be a word I want you to reverse. 
To reverse it, I want you to add a hyphen between each letter. Then reverse it. After that, remove the hyphens from the reversed word.
입력 출력의 각 문자열 길이는 같아야 한다. 

<example>
input: webdesign
hyphen separated characters: w-e-b-d-e-s-i-g-n
hyphen separated reversed characters: n-g-i-s-e-d-b-e-w
output: ngisedbew
</example>

<example>
input: http
hyphen separated characters: h-t-t-p
hyphen separated reversed characters: p-t-t-h
output: ptth
</example>

<example>
input: status
hyphen separated characters: s-t-a-t-u-s
hyphen separated reversed characters: s-u-t-a-t-s
output: sutats
</example>
"""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0.5},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)