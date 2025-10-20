from PaperCleaner import read_all_pdfs_in_folder_and_clean
from PaperProcessor import extract_paper_info, extract_paper_reference
from DataModel import Paper, json_to_paper, print_paper, full_json_to_paper, paper_to_json
from Utils import truncate_string
import json
import os
import csv

if __name__ == "__main__":
    paper_folder = "data/papers/ICSA/"
    output_folder = "temp/cleaned_papers"
    filem_metadata   = read_all_pdfs_in_folder_and_clean(paper_folder)
    
    papers = []
    for md in filem_metadata:
        #if metadata_location file already exists, skip
        paper_data_json = {}
        if os.path.exists(md.metadata_location):
            paper_data_json = json.load(open(md.metadata_location))
            print("metadata loaded from file", md.metadata_location)
            #print("paper_data_json=", truncate_string(json.dumps(paper_data_json, indent=4)))
            print("before full_json_to_paper")
            paper = full_json_to_paper(paper_data_json)
            print("after full_json_to_paper")
        else:
            # Extract paper information
            paper_info_json = extract_paper_info(md.content)
            
            # Extract references
            reference_json = extract_paper_reference(md.content)

            paper = json_to_paper(paper_info_json, reference_json)
            
            with open(md.metadata_location, "w") as file:
                #write json to file
                paper_as_json = paper_to_json(paper)
                json.dump(paper_as_json, file)
                print("wrote to file", md.metadata_location, "\n")
        papers.append(paper)
        print("before print_paper")
        print_paper(paper)
        print("after print_paper")
    
    #save papers to csv

    with open("temp/papers.csv", "w") as f1:
        pwriter = csv.writer(f1)
        pwriter.writerow(["title", "abstract", "mainIdea", "howItWorks", "benchmarks", "modelsOrAlgorithms", "hardware"])
        with open("temp/references.csv", "w") as f2:
            rwriter = csv.writer(f2)
            rwriter.writerow(["src_title", "target_title", "year", "venue", "authors"])
            for paper in papers:
                pwriter.writerow([paper.title, paper.abstract, paper.mainIdea, paper.howItWorks, paper.benchmarks, paper.modelsOrAlgorithms, paper.hardware])
                for reference in paper.references:
                    rwriter.writerow([paper.title, reference.title, reference.year, reference.venue, reference.authors])
    print("papers saved to csv")

        

