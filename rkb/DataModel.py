from dataclasses import dataclass

@dataclass
class Reference:
    title: str
    year: str
    venue: str
    authors: str

@dataclass
class Paper:
    title: str
    abstract: str
    mainIdea: str
    howItWorks: str
    benchmarks: list[str]
    modelsOrAlgorithms: list[str]
    hardware: list[str]
    references: list[Reference]
    paper_id: str

@dataclass
class PaperFile:
    location: str
    metadata_location: str
    content: str
    llm_response: str


sample_json = {
    "title": "Data Accesscentered Understanding of Microservices Architectures",
    "abstract": "This paper introduces an approach for systematically analyzing data access code fragments in complex applications composed of multiple microservices and distributed across several codebases, combining heuristic-based code analysis with natural language processing to identify, extract, interpret, and document interactions between microservices and their databases.",
    "mainIdea": "The main idea is to statically recover a view of data access in a microservices architecture by generating a detailed report analyzing API and database interactions between microservices, considering both code and data layers.",
    "How it works?": "The approach involves a 6-step process: Acquisition, Initialization, Identification (using heuristics and CodeQL), Extraction, Interpretation (using NLP), and Presentation (generating a report).",
    "What benchmarks are used?": "The paper evaluates the approach on 5 different microservices architectures found in benchmarks and on GitHub, targeting JavaScript projects relying on MongoDB and/or Redis databases.",
    "What models or algorithms are used?": "The approach uses heuristic-based code analysis, abstract syntax tree (AST) analysis, CodeQL for static analysis, and natural language processing (NLP) with Natural 25 and winkJS 26 libraries for interpreting data-related samples.",
    "What hardware is used?": "The paper does not explicitly mention the hardware used.",
    "references": {
        "references": [
            {
                "title": "Microservices Patterns with Examples in Java",
                "year": "2018",
                "venue": "Simon and Schuster",
                "citation": "C Richardson Microservices Patterns with Examples in Java  Simon and Schuster 2018"
            }
        ]
    }
}

#this parses the json responed proveded by the llm
def json_to_paper(json_data: dict, references_json: dict) -> Paper:
    paper = Paper(
        title=json_data["title"],
        abstract=json_data["abstract"],
        mainIdea=json_data["mainIdea"],
        howItWorks=json_data["How it works?"],
        benchmarks=json_data["What benchmarks are used?"],
        modelsOrAlgorithms=json_data["What models or algorithms are used?"],
        hardware=json_data["What hardware is used?"],
        references=[],
        paper_id=""
    )
    print("references_json=", references_json)
    #check is json has key "references"
    if "references" in references_json:
        references_json = references_json["references"]
    else:
        references_json = references_json
    
    for r in references_json:
        if "reference" in r:
            item = r["reference"]
        else:
            item = r
        
        paper.references.append(Reference(
            title=item["title"],
            year=item["year"],
            venue=item["venue"],
            authors=item["authors"]
        ))
    return paper

#this parses the json file saved
def full_json_to_paper(json_data: dict) -> Paper:
    # Create a list to store Reference objects
    references_list = []
    
    # Process references if they exist
    if "references" in json_data and json_data["references"]:
        for reference in json_data["references"]:
            references_list.append(Reference(
                title=reference["title"],
                year=reference["year"],
                venue=reference["venue"],
                authors=reference["authors"]
            ))
    
    # Create and return the Paper object
    paper = Paper(
        title=json_data["title"],
        abstract=json_data["abstract"],
        mainIdea=json_data["mainIdea"],
        howItWorks=json_data["howItWorks"],
        benchmarks=json_data["benchmarks"],
        modelsOrAlgorithms=json_data["modelsOrAlgorithms"],
        hardware=json_data["hardware"],
        references=references_list,
        paper_id=json_data.get("paper_id", "")
    )
    return paper

def paper_to_json(paper: Paper) -> dict:
    paper_json = {
        "title": paper.title,
        "abstract": paper.abstract,
        "mainIdea": paper.mainIdea,
        "howItWorks": paper.howItWorks,
        "benchmarks": paper.benchmarks,
        "modelsOrAlgorithms": paper.modelsOrAlgorithms,
        "hardware": paper.hardware,
        "references": []
    }
    for reference in paper.references:
        paper_json["references"].append({
            "title": reference.title,
            "year": reference.year,
            "venue": reference.venue,
            "authors": reference.authors
        })
    return paper_json

def print_paper(paper: Paper):
    print("Title:", paper.title, ", Abstract:", paper.abstract, ", Main Idea:", paper.mainIdea, ", How It Works:", paper.howItWorks, 
        ", Benchmarks:", paper.benchmarks, ", Models or Algorithms:", paper.modelsOrAlgorithms, ", Hardware:", paper.hardware, ", References:", paper.references)
    for reference in paper.references:
        print("Reference:", reference.title, ", Year:", reference.year, ", Venue:", reference.venue, ", authors:", reference.authors)

