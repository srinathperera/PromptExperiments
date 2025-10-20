import json
from DataModel import json_to_paper, print_paper

base = {
    "title": "Architecture and Performance Antipatterns Correlation in Microservice Architectures",
    "abstract": "This paper presents an empirical assessment of architecture antipattern detection in combination with the identification of performance issues using DV8 for architecture and PPTAM for performance, observing the co-occurrence of architectural Clique and performance Blob antipatterns and noting the strong correlation between normalized distance performance metric and architecture coupling values.",
    "mainIdea": "The main idea is to empirically assess the correlation between architectural and performance issues in microservice architectures, using tools like DV8 and PPTAM to identify antipatterns and analyze their relationship.",
    "How it works?": "The paper uses a framework involving service level metric objectives, high-level models, operational profile definitions, automated load test generation, software architecture assessment, and identification of architecture components to assess performance and scalability.",
    "What benchmarks are used?": "The Train Ticket benchmark microservice system is used.",
    "What models or algorithms are used?": "It uses DV8 for architecture antipattern detection and PPTAM for performance analysis, along with statistical measures like Pearson correlation, Spearman correlation, Normalized Mutual Information (NMI), and Cosine similarity.",
    "What hardware is used?": "The hardware includes a Linux virtual machine with 8 GB RAM and 4 logical CPUs for the Drive component of PPTAM, and another Linux virtual machine with 64 GB RAM and 8 logical CPUs for the Testbed component (Train Ticket system) deployed in a Minikube environment."
}


references = {
    "references": [
    {
        "reference": {
            "title": "Characteristics of scalability and their impact on performance",
            "year": "2000",
            "venue": "Second International Workshop on Software and Performance (WOSP)",
            "citation": "Andre B Bondi Characteristics of scalability and\ntheir impact on performance In Second International\nWorkshop on Software and Performance WOSP 2000\nOttawa Canada September 1720 2000  pages 195\n203 ACM 2000"
        }
    },
    {
        "reference": {
            "title": "A metric for predicting the performance of an application under a growing workload",
            "year": "2002",
            "venue": "IBM Systems Journal",
            "citation": "Elaine J Weyuker and Alberto Avritzer A metric for\npredicting the performance of an application under a\ngrowing workload IBM Syst J  4114554 2002"
        }
    }]
}

merged = base | references

print(json.dumps(merged, indent=4))

paper = json_to_paper(merged)
print_paper(paper)