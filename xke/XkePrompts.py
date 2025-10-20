
from haystack.dataclasses import ChatMessage

from XkeUtils import json2str

common_instructions = """"\" Let's think step by step. 
Please provide the response in JSON in following format
{
  "type": "object",
  "properties": {
    "answer": {
      "type": "string",
      "description": "put your answer here"
    },
    "thinking": {
      "type": "string",
      "description": "put your step by step thinking/critic here",
    }
  },
  "required": ["answer", "thinking"]
}
DATA: \n{{contet_text}}\n"Answer in JSON format.Do not write anything outside JSON, """



def get_first_promot(question, context_text):
    p1_q_prefix = "Instructions: Answer \""
    p1_q_suffix = "\" using DATA given below. "

    prompt_template = [
        ChatMessage.from_system("You are a expert document analyser."),
        ChatMessage.from_user(p1_q_prefix + question + " " + p1_q_suffix + common_instructions)
    ]

    return prompt_template

def get_iterative_promot(question, details_txt):
    prompt2_prefix = "Following JSON provides the answer to " + question + " considering DATA and thinking to make that decision. Please critic the answer and improve the answer."
    prompt2 = prompt2_prefix + details_txt + common_instructions 

    prompt_template = [
        ChatMessage.from_system("You are a expert document analyser."),
        ChatMessage.from_user(prompt2)
    ]

    return prompt_template
