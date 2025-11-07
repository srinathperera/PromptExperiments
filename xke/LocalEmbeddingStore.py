import json
import numpy as np
from xke.XkeUtils import get_embedding_via_rest_client
import time

#LOCAL_EMBEDDING_STORE_FILE = "/Users/srinath/code/PromptExperiments/data/my_embeddings.jsonl"
LOCAL_EMBEDDING_STORE_FILE = "data/my_embeddings.jsonl"
EMBEDDING_CACHE = {}

def init_local_embedding_store():
    #load saved embeddings from local file
    with open(LOCAL_EMBEDDING_STORE_FILE, 'r') as f:
        for line in f:
            loaded_item = json.loads(line)
            # Optional: Convert the list back to a NumPy array
            np_embedding = np.array(loaded_item["embedding"])
            EMBEDDING_CACHE[loaded_item["text"]] = np_embedding
    print(f"Loaded {len(EMBEDDING_CACHE)} embeddings from local store")


# 1. Your data (example)
data_to_save = [
    {"text": "Hello world", "embedding": np.array([0.1, 0.2, 0.3])},
    {"text": "This is a test", "embedding": np.array([0.4, 0.5, 0.6])},
    {"text": "Another sentence", "embedding": np.array([0.7, 0.8, 0.9])}
]

"""
# 2. How to Write to a .jsonl file
with open('my_embeddings.jsonl', 'w') as f:
    for item in data_to_save:
        # Convert NumPy array to a plain list for JSON serialization
        item_to_write = {
            "text": item["text"],
            "embedding": item["embedding"].tolist() 
        }
        # Write the JSON object as a single line
        f.write(json.dumps(item_to_write) + '\n')

print("Saved to my_embeddings.jsonl")


print(f"Loaded {len(loaded_data)} items.")
print(loaded_data[0])
"""

def clean_string(string):
    string = string.strip().lower()
    if string == '':
        return 'empty'
    return string

def add_embedding_to_local_store(strings_to_embed):
    for index, string in enumerate(strings_to_embed):
        strings_to_embed[index] = clean_string(string)
    #remove duplicates
    strings_to_embed = list(set(strings_to_embed))

    strings_not_in_cache = []
    for string in strings_to_embed:
        if string not in EMBEDDING_CACHE:
            strings_not_in_cache.append(string)
    
    if len(strings_not_in_cache) > 0:
        embeddings_for_missing_strings = []

        #call api for 100 strings at a time
        for i in range(0, len(strings_not_in_cache), 100):
            strings_to_embed = strings_not_in_cache[i:min(i+100, len(strings_not_in_cache))]
            new_embeddings = get_embedding_via_rest_client(strings_to_embed)
            assert len(new_embeddings) == len(strings_to_embed), f"Number of embeddings for missing strings does not match number of strings to embed: {len(embeddings_for_missing_strings)} != {len(strings_to_embed)}"
            embeddings_for_missing_strings.extend(new_embeddings)
            time.sleep(70)
            print(f"Sleeping for 70 seconds after calling API for {len(strings_to_embed)}/{len(strings_not_in_cache)}")

        #if len(strings_not_in_cache) > 100:
        #    raise ValueError(f"Too many strings to embed: {len(strings_not_in_cache)}")
        #embeddings_for_missing_strings = get_embedding_via_rest_client(strings_not_in_cache)
        #assert len(embeddings_for_missing_strings) == len(strings_not_in_cache), f"Number of embeddings for missing strings does not match number of strings to embed: {len(embeddings_for_missing_strings)} != {len(strings_not_in_cache)}"
        
        with open(LOCAL_EMBEDDING_STORE_FILE, 'a') as f:
            for i in range(len(strings_not_in_cache)):
                #print(f"Adding embedding for {strings_not_in_cache[i]}", embeddings_for_missing_strings[i][:5], type(embeddings_for_missing_strings[i]))
                np_embedding = np.array(embeddings_for_missing_strings[i])
                EMBEDDING_CACHE[strings_not_in_cache[i]] = np_embedding
                f.write(json.dumps({"text": strings_not_in_cache[i], "embedding": embeddings_for_missing_strings[i]}) + '\n')
                
    print(f"Added {len(strings_not_in_cache)} embeddings to local store")
        

def get_embedding_from_local_store(string_to_embed):
    string_to_embed = clean_string(string_to_embed)
    if string_to_embed in EMBEDDING_CACHE:
        return EMBEDDING_CACHE[string_to_embed]
    else:
        raise ValueError(f"Embedding for {string_to_embed} not found in local store, you must add it first using add_embedding_to_local_store")

init_local_embedding_store()

if __name__ == "__main__":
    
    add_embedding_to_local_store(["Hello world", "This is a test", "Another sentence"])
    print(get_embedding_from_local_store("Hello world")[:5])
    print(get_embedding_from_local_store("This is a test")[:5])
    print(get_embedding_from_local_store("Another sentence")[:5])
    #print(get_embedding_from_local_store("Not in cache"))