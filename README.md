# GraphWithLLM
## Structure
The project is divided into these main parts:
1. The `src` folder contains the external files of the project.
2. The code files on root level are the main files of the project.
3. The `DB` folder contains the files for the database.

## Src Folder
The `src` folder needs the following files:
- For the ESCO Skills:
  1. Folder `ESCO` - Contains the ESCO Skills in different csv Files
  2. Folder `Output` - Contains the output files.
- For the Modules:
  1. Folder `Modules` - Contains the Modules in pdf format.
- For the AI:
  1. Folder `Prompts` - Contains the Prompts for the AI.
- For the config:
    1. `general.yml` - Contains the configuration for the program. You can add your own configuration in this folder.
- In order to use the project parts individually and for better traceability:
    1. Folder `Cache` - Contains the results of the individual steps.

## Example Files

### config
```yaml
Modulestructure:
  FormalDetails:
    - Formal Details of the Module
    - FORMALE ANGABEN ZUM MODUL
  TeachingMethods:
    - EINGESETZTE LEHRFORMEN
    - Teaching Methods
  Examination:
    - Forms of Examination
    - EINGESETZTE PRÜFUNGSFORMEN
...
LLM_Structure:
  Nodes:
    - Name: Program
      Properties:
        - name
        - level
        - totalETCS
      Edges:
        - Target: Module
          Properties:
            - contains

    - Name: Module
      Properties:
        - code
        - name
        - year
        - mandatory
        - ETCS
        - language
      Edges:
        - Target: Module
          Properties:
            - requires
        - Target: Unit
          Properties:
            - consists_of
        - Target: Assessment
          Properties:
            - assessed_by
        - Target: Skill
          Properties:
            - needs_skill
            - develops_skill

    - Name: Unit
...
Ignored_Properties_Merging:
  - code
Ignored_Nodes_Merging:
  - Assessment
Caching:
  Graph_JSON: Graph_JSON.json
  Merged_Graph_JSON: Merged_Graph_JSON.json
  LLM_Graph: LLM_Graph.txt
...
LLM:
  Model: gemini-2.0-flash
  Temperature: 1
  Top_p: 0.95
  Top_k: 40
  Max_Output_Tokens: 8192
  Response_Mime_Type: application/json
```
- The `Modulestructure` contains the structure of the Modules in the pdf files. You can add headings in the desired language.
- The `LLM_Structure` contains the structure of the graph.
- The `Ignored_Properties_Merging` contains the properties that should be ignored when merging the graphs.
- The `Ignored_Nodes_Merging` contains the nodes that should be ignored when merging the graphs.
- The `Caching` contains the files that will be cached, you can change the names of the files to your liking.
- The `LLM` contains the information for the LLM API.

##### Config Structure
- Modulestructure: Contains the structure of the Modules in the pdf files. You can add headings in the desired language.
- LLM_Structure: Contains the structure of the graph. You can add nodes and edges with their properties.
- Ignored_Properties_Merging: Contains the properties that should be ignored when merging the graphs.
- Ignored_Nodes_Merging: Contains the nodes that should be ignored when merging the graphs.
- Caching: Contains the files that will be cached, you can change the names of the files to your liking.
- LLM: Contains the information for the LLM API

### What can the program do?
- ESCO DB
  1. The Program will setup da Database in the docker container with the Structure of 'DB/init.sql'. 
  2. Then it will automatically insert all the ESCO Skills in the DB. It will use all csv files in the ESCO folder no matter what names the files have.
  3. Extract preferred labels and descriptions from the DB and save them in a new csv file.
- Modules
  1. Extract the Modules from the pdf files and build a json structure in a useful way.
- Merging Graphs
  1. Merge the graphs into one graph. The graphs are in the `Cache` folder in a json format. The system will detect duplicates, merge them and save the result in the `Cache` folder.

### How to use the program?
#### Setup
1. Install python3 and the required packages
2. Create the folder Structure as described in the following section.
3. Use the `general.yml` file to configure the program or create your own config file.
4. Get a module and store it in the `Modules` folder. The file has to start with the first module, because the table of contents cant be detected.
5. Check the prompts in the `Prompts` folder.
6. Get the ESCO Skills and store them in the `ESCO` folder. They can be stored in multiple csv files.
7. The projects needs a .env file with the following content. The file has to be in the `DB` folder:
  ```env
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_PORT=
DB_HOST=
API_KEY=
  ```

#### Run
You have to run the `main.py` file. You can use the following flags:
- `--escodb` to setup the ESCO DB and insert the data.
- `--extractpdf` to extract the Modules from the pdf files. Value is the filename.
- `--escolabel` read ESCO-DB and extract preferred label and description.
- `--all` to run all the functions at once. This command isnt recommended because it will take a long time and gemini is more likely to do errors. If you want to run it, you also have to use the `--extractpdf` flag to define your module file.
- `--config` to use a different config file. Value is the filename. Default is `general.yml`. Your own config needs the same structure as the `general.yml`.
- `--merge` to merge graphs into one.
- `--folderstructure` to create the folder structure for the project.
- `--connectesco` connect esco with skills in graph
- `--createcipher` to create the cipher for the graph.
- `--createjsongraph` create json graph from pdf json

#### Results
The different results of each step will be saved in the `Cache` folder. The final result will be saved in the `Cache` folder. The name of the file is defined in the config file with the key `LLM_Graph`.
