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

from XkePrompts import get_first_promot
from XkePrompts import get_iterative_promot
from XkeUtils import truncate_string, json2str
VERBOSE = True


from dataclasses import dataclass
@dataclass
class Answer:
    answer: str
    thinking: str
    confidence: float
    def to_json(self):
        return {
            "answer": self.answer,
            "thinking": self.thinking,
            "confidence": self.confidence
        }
    
@dataclass
class SolutionMetadata:
    answers: list[Answer] = None
    
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


def run_iteration(question, context_text):
    itr_count = 5
    smd = SolutionMetadata()
    # Build a RAG pipeline
    prompt_template = get_first_promot(question, context_text)
    p1_json_response = call_llm(prompt_template, context_text)
    smd.answers.append(Answer(thinking=p1_json_response['thinking'], answer=p1_json_response['answer'], confidence=0.7))

    for i in range(itr_count -1):
        prompt_template = get_iterative_promot(question, json2str(smd.to_json()))
        p2_json_response = call_llm(prompt_template, context_text)
        #check if thinking and answer are present in the response
        print(json2str(p2_json_response))
        if 'thinking' in p2_json_response and 'answer' in p2_json_response:
            smd.answers.append(Answer(thinking=p2_json_response['thinking'], answer=p2_json_response['answer'], confidence=0.7))
        else:
            print("Thinking and answer are not present in the response, itrating again")
            continue
        print(i, json2str(p2_json_response["answer"]))

    print(json2str(smd.to_json()))

    #TODO use another promot to find the best answer among the answers
    #prompt_template = get_best_answer_promot(question, json2str(smd.to_json()))
    #p3_json_response = call_llm(prompt_template, context_text)
    #print(json2str(p3_json_response))

    ## we can build a classifer to select the best answer among the answers
    # one idea is to find the avg emebdding and find the answer with the most similar embedding

    


def call_llm(prompt_template, contet_text):
    # Define required variables explicitly
    prompt_builder = ChatPromptBuilder(template=prompt_template, required_variables={"contet_text"})

    llm = GoogleGenAIChatGenerator(api_key=Secret.from_env_var("GEMINI_API_KEY"))

    rag_pipeline = Pipeline()
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("prompt_builder", "llm.messages")

    # Ask a question
    results = rag_pipeline.run(
        {
            "prompt_builder": {"contet_text": contet_text},
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

file_path = "data/article_cloudflare.txt"
#read file as text
with open(file_path, 'r') as file:
    article_text = file.read()
    question = "What is the main idea about this article?"
    run_iteration(question, article_text)

