# GraphWithLLM
## Structure
The project is divided into 2 main parts:
1. The `src` folder contains the external files of the project.
2. The code files on root level are the main files of the project.

## Src Folder
The `src` folder needs the following files:
1. `LLM_Angaben.yml` - Contains the graph structure.
2. `LLM_Graph.txt` - Contains the graph data (Cipher for Neo4j).


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
1. Check the Graph structure of the txt file based on the yml structure. For the Moment only Edges can be checked.
2. If edges have been deleted, the program will show the edges, delete them and checks the syntax of the cipher.

