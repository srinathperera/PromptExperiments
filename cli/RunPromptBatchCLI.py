import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.PromptUtils import call_llm
import json
from haystack.dataclasses import ChatMessage
import pandas as pd

def run_prompt_batch(prompt_template, data_array):
    results = []
    for data in data_array:
        result = call_llm(prompt_template, data)
        results.append(result)
    return results
    #save results to json file
    
def run_prompt_batch_from_file(file_path):
    with open("prompts/GradePrompts.txt", "r") as f:
        prompt = f.read()
    
    with open(file_path, 'r') as f:
        data_array = pd.read_json(f)
        
    print("File reading complete")

    data_array = data_array[:3]

    prompt_template = [
        ChatMessage.from_system("You are a expert Assistant"),
        ChatMessage.from_user(prompt)
    ]
    
    results = run_prompt_batch(prompt_template, data_array)

    results_path = file_path.replace('.json', '_results.json')

    with open(results_path, 'w') as f:
        json.dump(results, f)

    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    run_prompt_batch_from_file(file_path='/Users/srinath/code/ExploreData/data/promot_additional_data.json')
