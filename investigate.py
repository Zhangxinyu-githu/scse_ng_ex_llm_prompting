## Import the necessary modules
import json
import ollama
from parse_data import load_items, get_unclaimed_items, save_result
## Import the function from the module parse_data


## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.

def build_prompt(description, available_items):
    system_prompt = ""
    user_prompt = ""
    return system_prompt, user_prompt

    
## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    response = ollama.chat(
            model='qwen',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ]
        )
    return response['message']['content']

## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != -1:
            result = json.loads(response_text[start:end])
        else:
            result = {"matches": [], "confidence": "LOW"}
    return result
        


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    valid_ids = {item['id'] for item in available_items}
    valid_confidences = {"LOW", "MEDIUM", "HIGH"}

    if not isinstance(result, dict):
        return False
    if "matches" not in result or "confidence" not in result:
        return False
    if not isinstance(result["matches"], list):
        return False
    if result["confidence"] not in valid_confidences:
        return False
    
    for item_id in result["matches"]:
        if item_id not in valid_ids:
            return False
            
    return True


## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    print(f"Confidence: {result['confidence']}")
    
    if not result["matches"]:
        print("No matches were found.")
        print(f"Matches: {result['matches']}")
        return

    print("Possible matches:")
    items_dict = {item['id']: item for item in available_items}
    
    for item_id in result["matches"]:
        item = items_dict.get(item_id)
        if item:
            print("-" * 40)
            print(f"ID: {item['id']}")
            print(f"Item: {item['item']}")
            print(f"Color: {item['color']}")
            print(f"Location: {item['location']}")
            print(f"Date found: {item['date']}")
    

## Control center for the entire program.
def main():
    all_items = load_items('found_items.json')
    unclaimed_items = get_unclaimed_items(all_items)
        
    description = input("Describe the item you lost: ")
    print("Searching for possible matches...")
        
    system_prompt, user_prompt = build_prompt(description, unclaimed_items)
        
    response_text = ask_qwen(system_prompt, user_prompt)
        
    result = parse_response(response_text)
    is_valid = validate_result(result, unclaimed_items)
        
    if not is_valid:
            print("The model returned an invalid response. Using a default empty result.")
            result = {"matches": [], "confidence": "LOW"}
    
    display_matches(result, unclaimed_items)
        
    save_result(result, 'output/match_result.json')
    print(f"Result saved to output/match_result.json")


if __name__ == "__main__":
    main()
