import re
from haystack import Pipeline
from haystack.utils import Secret
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.dataclasses import ChatMessage
from PaperCleaner import clean_all_pdfs_in_folder
import json
from Utils import truncate_string

def read_cleaned_text(file_path):
    """Read the content of a cleaned text file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_paper_info(cleaned_paper_text):
    # Build a RAG pipeline
    prompt_template = [
        ChatMessage.from_system("You are a helpful assistant."),
        ChatMessage.from_user(
            "Given the following paper, extract information in following JSON format.\n"
            "Only use information from the paper, do not make up any information.\n"
             "Answer each fild in short from, never use more than one sentence. Do not write anything outside JSON.: \n"
            "json_schema: \n"
            "{\n"
            "    \"title\": \"string\",\n"
            "    \"abstract\": \"string\",\n"
            "    \"mainIdea\": \"string\",\n"
            "    \"How it works?\": \"string\",\n"
            "    \"What benchmarks are used?\": \"string\",\n"
            "    \"What models or algorithms are used?\": \"string\",\n"
            "    \"What hardware is used?\": \"string\",\n"
            "}\n"
            "Paper:\n{{cleaned_paper_text}}\n"
            "Answer in JSON format:"
        )
    ]

    # Define required variables explicitly
    prompt_builder = ChatPromptBuilder(template=prompt_template, required_variables={"cleaned_paper_text"})

    llm = GoogleGenAIChatGenerator(api_key=Secret.from_env_var("GEMINI_API_KEY"))

    rag_pipeline = Pipeline()
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("prompt_builder", "llm.messages")

    # Ask a question
    results = rag_pipeline.run(
        {
            "prompt_builder": {"cleaned_paper_text": cleaned_paper_text},
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


def extract_paper_reference(cleaned_paper_text):
    # Build a RAG pipeline
    prompt_template = [
        ChatMessage.from_system("You are a helpful assistant."),
        ChatMessage.from_user(
            "Given the following paper, extract paperes referend by the paper in following JSON format.\n"
            "Only use information from the paper, do not make up any information.\n"
             "Do not write anything outside JSON.: \n"
            "json_schema: \n"
            "{\n"
            "    \"reference\": {\n"
            "        \"title\": \"string\",\n"
            "        \"year\": \"string\",\n"
            "        \"venue\": \"string\",\n"
            "        \"authors\": \"string\",\n"
            "    }\n"
            "}\n"
            "Paper:\n{{cleaned_paper_text}}\n"
            "Answer in JSON format:"
        )
    ]

    # Define required variables explicitly
    prompt_builder = ChatPromptBuilder(template=prompt_template, required_variables={"cleaned_paper_text"})

    llm = GoogleGenAIChatGenerator(api_key=Secret.from_env_var("GEMINI_API_KEY"))

    rag_pipeline = Pipeline()
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("prompt_builder", "llm.messages")

    # Ask a question
    results = rag_pipeline.run(
        {
            "prompt_builder": {"cleaned_paper_text": cleaned_paper_text},
        }
    )
    reply = results["llm"]["replies"][0]
    reply_content = reply.text
    
    # Extract JSON from response (remove markdown formatting if present and considering arrays as well)
    reply_content = reply_content.replace("```json", "").replace("```", "")
    print(reply_content)

    json_str = reply_content
    try:
        result = json.loads(json_str)
        print("result=", result)
        return result
    except json.JSONDecodeError as e:
        raise Exception("Failed to parse JSON", e, truncate_string(json_str))


    
