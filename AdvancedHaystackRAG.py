from haystack import Pipeline, Document
from haystack.utils import Secret
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.retrievers.in_memory import InMemoryBM25Retriever
from haystack_integrations.components.generators.google_genai import GoogleGenAIChatGenerator
from haystack.components.builders.chat_prompt_builder import ChatPromptBuilder
from haystack.dataclasses import ChatMessage

from haystack_integrations.document_stores.chroma import ChromaDocumentStore
from haystack_integrations.components.retrievers.chroma import ChromaQueryTextRetriever
from haystack import Document
from haystack import component

def createChromaDocumentStore():
    # this is in memory document store, see https://docs.haystack.deepset.ai/docs/chromadocumentstore for more details
    document_store = ChromaDocumentStore()

    document_store.write_documents([
    Document(content="My name is Emily and I live in Paris."),
    Document(content="My name is Jean and I live in Paris."),
    Document(content="My name is Mark and I live in Berlin."),
    Document(content="My name is Giorgio and I live in Rome.")
    ])
    return document_store


# this custom componet added new facts 
@component
class DocEnhancerComponent:
  @component.output_types(documents=list)
  def run(self, documents:list):
    #print("documents", documents)
    documents.append(Document(content="My name is Pierre and I live in Paris."))
    return {"documents": documents}

    

# Write documents to InMemoryDocumentStore
#document_store = InMemoryDocumentStore()
document_store = createChromaDocumentStore()

# Build a RAG pipeline
prompt_template = [
    ChatMessage.from_system("You are a helpful assistant."),
    ChatMessage.from_user(
        "Given these documents, answer the question.\n"
        "Documents:\n{% for doc in documents %}{{ doc.content }}{% endfor %}\n"
        "Question: {{question}}\n"
        "Answer:"
    )
]

# Define required variables explicitly
# we can use similar method to add custom functions etc 
prompt_builder = ChatPromptBuilder(template=prompt_template, required_variables={"question", "documents"})

#retriever = InMemoryBM25Retriever(document_store=document_store)
retriever = ChromaQueryTextRetriever(document_store=document_store)
#llm = OpenAIChatGenerator(api_key=Secret.from_env_var("OPENAI_API_KEY"))
llm = GoogleGenAIChatGenerator(api_key=Secret.from_env_var("GEMINI_API_KEY"))

rag_pipeline = Pipeline()
rag_pipeline.add_component("retriever", retriever)
rag_pipeline.add_component("prompt_builder", prompt_builder)
rag_pipeline.add_component("llm", llm)
#rag_pipeline.connect("retriever", "prompt_builder.documents")
#rag_pipeline.connect("prompt_builder", "llm.messages")

enhancer_component = DocEnhancerComponent()
rag_pipeline.add_component("enhancer", enhancer_component)
rag_pipeline.connect("retriever", "enhancer.documents")
rag_pipeline.connect("enhancer.documents", "prompt_builder.documents")
rag_pipeline.connect("prompt_builder", "llm.messages")





# Ask a question
question = "Who lives in Paris?"
results = rag_pipeline.run(
    {
        "retriever": {"query": question},
        "prompt_builder": {"question": question},
    }
)
reply = results["llm"]["replies"][0]
reply_content = reply.text
print(reply_content)
