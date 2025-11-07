from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack import Pipeline
from haystack.utils import Secret
import json

def truncate_string(s, max_length=100):
    return s[:min(max_length, len(s))]

def call_llm(prompt_template, data_text) -> dict:
    # Define required variables explicitly
    prompt_builder = ChatPromptBuilder(template=prompt_template, required_variables={"DATA"})

    llm = GoogleGenAIChatGenerator(api_key=Secret.from_env_var("GEMINI_API_KEY"))

    rag_pipeline = Pipeline()
    rag_pipeline.add_component("prompt_builder", prompt_builder)
    rag_pipeline.add_component("llm", llm)
    rag_pipeline.connect("prompt_builder", "llm.messages")

    # Ask a question
    results = rag_pipeline.run(
        {
            "prompt_builder": {"DATA": data_text},
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