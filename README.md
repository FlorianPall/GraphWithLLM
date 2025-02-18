# GraphWithLLM
## Structure
The project is divided into these main parts:
1. The `src` folder contains the external files of the project.
2. The code files on root level are the main files of the project.
3. The `DB` folder contains the files for the database.

## Src Folder
The `src` folder needs the following files:
- For structure check:
  1. `LLM_Angaben.yml` - Contains the graph structure.
  2. `LLM_Graph.txt` - Contains the graph data (Cipher for Neo4j).
- For the ESCO Skills:
  1. Folder `ESCO` - Contains the ESCO Skills in different csv Files
  2. Folder `Output` - Contains the output csv files.
- For the Modules:
  1. Folder `Modules` - Contains the Modules in pdf format.
- For the AI:
  1. Folder `Prompts` - Contains the Prompts for the AI.

## LLM_Angaben.yml
```yaml
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
        ...
```

### LLM_Graph.txt
```txt
// Create Module
CREATE (m:Module {
  code: 'T4INF2003',
  name: 'Software Engineering I',
  year: 2,
  mandatory: true,
  ETCS: 9,
  language: ['Deutsch', 'Englisch']
})

// Create Units and Module-Unit relationships
WITH m
CREATE (spec:Unit {
  name: 'Specification',
  code: 'SPEC',
  hours: 90,
  delivery_mode: 'Lecture, Tutorial, Lab work'
}),
(design:Unit {
  name: 'Design',
  code: 'DESIGN',
  hours: 90,
  delivery_mode: 'Lecture, Tutorial, Lab work'
}),
...
```

### What can the program do?
- Structure
  1. Check the Graph structure of the txt file based on the yml structure. For the Moment only Edges can be checked.
  2. If edges have been deleted, the program will show the edges, delete them and checks the syntax of the cipher.
  3. The Result will be saved in a new file named `LLM_Graph_Output.txt`. This file will be written in the same directory as the input file. This will also be written if the input file is correct.
- ESCO DB
  1. The Programm will setup da Database in the docker container with the Structure of 'DB/init.sql'. 
  2. Then it will automaticaly insert all the ESCO Skills in the DB. It will use all csv files in the ESCO folder no matter what names the files have.
  3. Extract preferred labels and descriptions from the DB and save them in a new csv file.
- Modules
  1. Extract the Modules from the pdf files and build a json structure in a useful way.

### How to use the program?
You have to run the `main.py` file. You can use the following flags:
- `--escodb` to setup the ESCO DB and insert the data.
- `--extractpdf` to extract the Modules from the pdf files. Value is the filename.
- `--structure` to check the graph structure of the txt file.
- `--escolabel` read ESCO-DB and extract preferred label and description.
- `--all` to run all the functions at once.
