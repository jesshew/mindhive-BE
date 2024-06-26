from langchain.chat_models import ChatOpenAI
from langchain.agents import create_json_agent
from langchain.agents.agent_toolkits import JsonToolkit
from langchain.tools.json.tool import  JsonSpec
import json
import os

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
file_path='scraped_outlets.json'

def perform_llm_query(query):
    with open(file_path,"r") as f1:
        data=json.load(f1)
        f1.close()

    spec=JsonSpec(dict_=data,max_value_length=4000)
    toolkit=JsonToolkit(spec=spec)
    agent=create_json_agent(llm=ChatOpenAI(temperature=0,model="gpt-4o"),toolkit=toolkit,max_iterations=1000,verbose=True,handle_parsing_errors=True)
    # print(agent.run("what store closes the earliest ?"))

    try:
        response = agent.run(query)
        print(response)
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error: {str(e)}"
    # print(agent.run("how many stores are located in ground floor? list them all"))


# Function to write data to JSON file
def write_json_file(data_list):
    try:
        if not data_list:
            print("Data list is empty. Nothing to write.")
            return

        # Convert 'hours' list to a semicolon-separated string
        for item in data_list:
            if 'hours' in item and isinstance(item['hours'], list):
                item['hours'] = ";".join(str(v) for v in item['hours'])

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, ensure_ascii=False, indent=4)

        print(f"{len(data_list)} items successfully written to {file_path}")
    except Exception as e:
        print(f"Failed to write data to {file_path}: {e}")

def write_to_txt(data_list):
    try:
        if not data_list:
            print("Data list is empty. Nothing to write.")
            return

        with open(file_path_txt, 'w', encoding='utf-8') as f:
            for item in data_list:
                f.write(f"{str(item)}\n")

        print(f"{len(data_list)} items successfully written to {file_path}")
    except Exception as e:
        print(f"Failed to write data to {file_path}: {e}")


# loader = JSONLoader(
#     file_path='your_json_file.json',
#     jq_schema='.your_content_field',  # Adjust this based on your JSON structure
#     text_content=False
# )
# data = loader.load()
# pprint(data)

# loader = TextLoader(file_path_txt)
# data = loader.load()
# prompt= "which subway closes the latest"
# index=VectorstoreIndexCreator().from_loaders([data])
# response=index.query(prompt)
# print(response) 


# pprint(data)
#perform_llm_query("is the subway at UOA Bangsar open at 9am ?")
#perform_llm_query("how many subway stores are located on the ground floor ? list all the names and address")



