
from pypdf import PdfReader 
from DataModel import PaperFile
import os
import re

def link_cleaner(text):
    """
    Cleans links from the text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with links removed.
    """
    url_pattern = r'http\S+|www\S+|https\S+'
    return re.sub(url_pattern, '', text, flags=re.MULTILINE)

def quote_cleaner(text):
    """
    Cleans quotes from the text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with quotes standardized.
    """
    # Standardize quotes
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    return text

def remove_extra_whitespaces(text):
    """
    Removes extra whitespaces from the text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with extra whitespaces removed.
    """
    return ' '.join(text.split())

def remove_emojis(text):
    """
    Removes emojis from the text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with emojis removed.
    """
    return text.encode('ascii', 'ignore').decode('ascii')

def remove_symbols(text):
    """
    Removes special symbols from the text.

    Args:
        text (str): The input text.

    Returns:
        str: The text with special symbols removed.
    """
    return ''.join(char for char in text if char.isalnum() or char.isspace())



def text_cleaner(text):
    """
    Cleans the input text by removing links and standardizing quotes.

    Args:
        text (str): The input text.

    Returns:
        str: The cleaned text.
    """
    text = link_cleaner(text)
    text = quote_cleaner(text)
    # text = remove_extra_whitespaces(text)
    text = remove_emojis(text)
    text = remove_symbols(text)
    return text

def read_pdf_file(file_path):
    text_content = ""
    with open(file_path, "rb") as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text_content += page.extract_text() + "\n"
    
    return text_content

def clean_pdf_content(file_path):
    raw_text = read_pdf_file(file_path)
    cleaned_text = text_cleaner(raw_text)
    return cleaned_text

def save_cleaned_text(file_path, output_path):
    cleaned_text = clean_pdf_content(file_path)
    with open(output_path, "w") as file:
        file.write(cleaned_text)

def clean_all_pdfs_in_folder(folder_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    cleaned_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            print(f"Cleaning file: {filename}")
            pdf_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, f"cleaned_{filename}.txt")
            save_cleaned_text(pdf_path, output_path)
            print(f"Cleaned and saved: {output_path}")
            cleaned_files.append(output_path)
    return cleaned_files

def read_all_pdfs_in_folder_and_clean(folder_path):
    cleaned_files_data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            print(f"Reading file: {filename}")
            pdf_path = os.path.join(folder_path, filename)
            cleaned_text = clean_pdf_content(pdf_path)
            metadata_path = os.path.join(folder_path, f"metadata_{filename}.json")
            cleaned_files_data.append(PaperFile(location=pdf_path, metadata_location=metadata_path, content=cleaned_text, llm_response=""))
    return cleaned_files_data


if __name__ == "__main__":
    paper_folder = "papers"
    output_folder = "cleaned_papers"
    cleaned_files = clean_all_pdfs_in_folder(paper_folder, output_folder)
    print(f"Cleaned {len(cleaned_files)} files")
    print(f"Cleaned files: {cleaned_files}")