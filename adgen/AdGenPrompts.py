from haystack.dataclasses import ChatMessage

def get_design_promot():
    with open("prompts/GenArch.txt", "r") as f:
        common_instructions = f.read()
    
    #common_instructions = common_instructions.replace("@@SYSTEMPRPOMPT@@", question)
    
    prompt_template = [
        ChatMessage.from_system("You are a expert system architect"),
        ChatMessage.from_user(common_instructions)
    ]
    return prompt_template