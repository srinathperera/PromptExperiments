import ollama

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

text = read_file("data/textWithpapers.txt")




response = ollama.chat(
    model='gemma3:4b',
    messages=[
        {
            'role': 'user',
            'content': "Extract research paper titles and years from the following text: " + text,
        },
    ]
)

print(response['message']['content'])