import json

def simplify_competences(competences):
    return json.loads(simplify_competences_testing())

def translate_modules(modules):
    return modules

def connected_esco(skills):
    return json.loads(connect_esco_testing())



# TESTING
def simplify_competences_testing():
    return """{
          "Mathematik I (T4INF1001)": {
            "competences": [
              {
                "FACHKOMPETENZ": [
                  "The students can develop mathematical thinking and argumentation skills.",
                  "The students are able to demonstrate a basic understanding of discrete mathematics and linear algebra.",
                  "The students can apply this knowledge to problems in engineering sciences and computer science.",
                  "The students are able to describe scientific and technical processes using discrete mathematics and linear algebra.",
                  "The students can develop an understanding of the complexity of matrix calculations."
                ]
              },
              {
                "METHODENKOMPETENZ": [
                  "The students can apply logical thinking skills.",
                  "The students are able to structure problems clearly.",
                  "The students can develop creative and exploratory behaviors.",
                  "The students are able to demonstrate perseverance when solving mathematical problems."
                ]
              },
              {
                "PERSONALE UND SOZIALE KOMPETENZ": [
                  "The students can work independently on mathematical problems.",
                  "The students are able to communicate mathematical concepts to others."
                ]
              },
              {
                "ÜBERGREIFENDE HANDLUNGSKOMPETENZ": [
                  "The students can transfer mathematical principles to other disciplines.",
                  "The students are able to use mathematical tools to solve interdisciplinary problems."
                ]
              }
            ]
          },
          "Theoretische Informatik I (T4INF1002)": {
            "competences": [
              {
                "FACHKOMPETENZ": [
                  "The students can understand the theoretical foundations of propositional and predicate logic.",
                  "The students are able to understand formal specification of algorithms and classify them.",
                  "The students can master the model of logical programming and apply it."
                ]
              },
              {
                "METHODENKOMPETENZ": [
                  "The students can break down complex business applications through abstract thinking.",
                  "The students are able to apply logical reasoning and inference depending on the situation.",
                  "The students can develop solution strategies for complex problems."
                ]
              },
              {
                "PERSONALE UND SOZIALE KOMPETENZ": [
                  "The students can present logical concepts to others.",
                  "The students are able to work in teams to solve complex logical problems."
                ]
              },
              {
                "ÜBERGREIFENDE HANDLUNGSKOMPETENZ": [
                  "The students can communicate with experts and laypeople about topics in logic, logical inference, verification, and abstract thinking at a scientific level.",
                  "The students are able to apply logical reasoning skills to various interdisciplinary contexts."
                ]
              }
            ]
          }
        }"""

def connect_esco_testing():
    return """[["S1", "interpret mathematical information", "equivalent"], 
    ["S2", "algebra", "partOf"], 
    ["TESTSKILL", "use logic programming", "equivalent"], 
    ["S4", "think abstractly", "equivalent"], 
    ["S5", "communicate with a non-scientific audience", "contains"]]"""