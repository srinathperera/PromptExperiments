from haystack import Pipeline
from haystack.utils import Secret
from AdGenPrompts import get_design_promot
from AdGenUtils import sort_and_print_edges
import pandas as pd
import os
from pathlib import Path
# we need a benchmark 
# Sci NLP might work - https://arxiv.org/abs/2509.07801 ( check it's related work too)  https://github.com/AKADDC/SciNLP
#other benchmarks are in https://docs.google.com/document/d/1OgP8u2KgDmuehV3eqmSgfEF25u4pPSsxv7TRVjKsQVA/edit?tab=t.ga8oxoz2r58a

#if nothing works, we can use Gemini output manaully checked  as truth and try with smaller model 
# we can also use paper data extraction also  

# next step - try getting the main idea from the paper
# sample code and extraction code in here

#idea is to ask LLM for output as well as chain of throughts, 
# repatedly asking LLM with hisoyrical work information and ask to refine the output until it is correct.


from haystack import Pipeline
from haystack.utils import Secret

from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder

import json


VERBOSE = True


from dataclasses import dataclass
@dataclass
class ArchSolution:
    answer: json
    thinking: str
    confidence: float
    def to_json(self):
        return {
            "answer": self.answer,
            "thinking": self.thinking,
            "confidence": self.confidence
        }
    
@dataclass
class ArchSolunCollection:
    answers: list[ArchSolution] = None
    
    def __post_init__(self):
        if self.answers is None:
            self.answers = []
    def to_json(self):
        return {
            "answers": [answer.to_json() for answer in self.answers]
        }


def print_diff(answer1, answer2):
    import difflib
    lines1 = answer1.replace('.', '\n').splitlines(keepends=True)
    lines2 = answer2.replace('.', '\n').splitlines(keepends=True)
    # Generate the unified diff
    diff = difflib.unified_diff(
        lines1,
        lines2,
        fromfile='Original_String',
        tofile='Modified_String',
        lineterm='' # Suppress the trailing newlines for clean printing
    )
    print(''.join(diff))



#ideas 
# give our questions / ask to create questions 
# provide dfiferent contexts and ask 


#def run_iteration(question, context_text):
#    itr_count = 5
#    smd = ArchSolunCollection()
#    # Build a RAG pipeline
#    prompt_template = get_first_promot(question, context_text)
#    p1_json_response = call_llm(prompt_template, context_text)
#    smd.answers.append(Answer(thinking=p1_json_response['thinking'], answer=p1_json_response['answer'], confidence=0.7))

#    for i in range(itr_count -1):
#        prompt_template = get_iterative_promot(question, json2str(smd.to_json()))
#        p2_json_response = call_llm(prompt_template, context_text)
        #check if thinking and answer are present in the response
#        print(json2str(p2_json_response))
#        if 'thinking' in p2_json_response and 'answer' in p2_json_response:
#            smd.answers.append(Answer(thinking=p2_json_response['thinking'], answer=p2_json_response['answer'], confidence=0.7))
#        else:
#            print("Thinking and answer are not present in the response, itrating again")
#            continue
#        print(i, json2str(p2_json_response["answer"]))

#    print(json2str(smd.to_json()))


def run_simple_archgen(system_story):
    prompt_template = get_design_promot()
    p1_json_response = call_llm(prompt_template, system_story)
    #print(p1_json_response)
    return p1_json_response



def call_llm(prompt_template, contet_text):
    # Define required variables explicitly
    prompt_builder = ChatPromptBuilder(template=prompt_template, required_variables={"SYSTEMSTORY"})

    llm = GoogleGenAIChatGenerator(api_key=Secret.from_env_var("GEMINI_API_KEY"))

    rag_pipeline = Pipeline()
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("prompt_builder", "llm.messages")

    # Ask a question
    results = rag_pipeline.run(
        {
            "prompt_builder": {"SYSTEMSTORY": contet_text},
        }
    )
    reply = results["llm"]["replies"][0]
    reply_content = reply.text
    #print(reply_content)
    
    # Extract JSON from response (remove markdown formatting if present)
    json_start = reply_content.find('{')
    json_end = reply_content.rfind('}') + 1
    
    if json_start != -1 and json_end > json_start:
        json_str = reply_content[json_start:json_end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            raise Exception("Failed to parse JSON", e, json_str)
    else:
        raise Exception("No valid JSON found in response", truncate_string(json_str))

#file_path = "data/article_cloudflare.txt"
#read file as text
#with open(file_path, 'r') as file:
#    article_text = file.read()
#    question = "What is the main idea about this article?"
#    run_iteration(question, article_text)


def process_problem_list(problem_list, output_file_paths,log_file_path):
    with open(log_file_path, 'w') as output_log_file:

        for index, story in enumerate(problem_list):
            print(f"Processing {index}")
            output_log_file.write(f"Processing {file}\n")
            design = run_simple_archgen(story)
            output_file_path = output_file_paths[index]
            with open(output_file_path, 'w') as output_file:
                json.dump(design, output_file)
            output_log_file.write("Problem:\n")
            output_log_file.write(story)
            output_log_file.write("\n")
            output_log_file.write("Solution:\n")
            output_log_file.write("\n")
            output_log_file.write(json.dumps(design, indent=4))
            output_log_file.write("\n")
            output_log_file.write(sort_and_print_edges(design))
            output_log_file.write("\n")
            print(f"{index} Done")


input_dir = "/Users/srinath/code/arch-autogen/data/model-problems"
output_dir = "/Users/srinath/code/arch-autogen/solutions/model-problems-output/v1"  

output_log_file = os.path.join(output_dir, "output.txt")

problem_list = []
output_file_paths = []
for file in os.listdir(input_dir):
    file_name = file.split(".")[0]
    if file.endswith(".txt"):
        file_path = os.path.join(input_dir, file)
        with open(file_path, 'r') as file:
            story = file.read()
        problem_list.append(story)
        output_file_name = Path(file.name).stem + ".json"
        print(output_file_name)
        output_file_path = os.path.join(output_dir, output_file_name)
        output_file_paths.append(output_file_path)

process_problem_list(problem_list, output_file_paths, output_log_file)
print("Done")
