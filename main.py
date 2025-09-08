from Helper import csvFile, Files
from Pdf import pdfFile
import argparse
import Startup
from Graph import Graph, ESCO, MergeGraphs

necessary_folders = [
    './src/Cache',
    './src/ESCO',
    './src/Modules',
    './src/Output'
]



parser = argparse.ArgumentParser(description='pdf to graph')
parser.add_argument('--escodb', action='store_true', help='read esco csv and write to db')
parser.add_argument('--extractpdf', type=str, help='wandelt pdf in json um. example: --extractpdf=LLM_Angaben.pdf')
parser.add_argument('--escolabel', action='store_true', help='read ESCO-DB_Setup and extract preferred label and description')
parser.add_argument('--all', action='store_true', help='all flags')
parser.add_argument('--config', type=str, help='name of the config file')
parser.add_argument('--merge', action='store_true', help='merge graphs')
parser.add_argument('--folderstructure', action='store_true', help='creates the folder structure of the project')
parser.add_argument('--connectesco', action='store_true', help='connect esco with skills in graph')
parser.add_argument('--createcipher', action='store_true', help='create cipher query')
parser.add_argument('--createjsongraph', action='store_true', help='create json graph from pdf json')

args = parser.parse_args()
data = None

if args.config:
    Files.CONFIG = args.config

if args.folderstructure or args.all:
    print("##########Creating folder structure##########")
    Startup.folder_structure(necessary_folders)
if args.escodb or args.all:
    print("##########Reading esco csv and writing to db##########")
    csvFile.csv_to_db()
if args.extractpdf:
    print("##########Extracting pdf##########")
    data = pdfFile.extract_pdf(args.extractpdf, data)
if args.createjsongraph or args.all:
    print("##########Creating json graph##########")
    data = Graph.create_json_graph(data)
if args.escolabel or args.all:
    print("##########Reading ESCO-DB_Setup and extracting preferred label and description##########")
    csvFile.export_preferred_label()
if args.merge or args.all:
    print("##########Merging graphs##########")
    MergeGraphs.merge()
if args.connectesco or args.all:
    print("##########Connecting esco with skills in graph##########")
    data = ESCO.connect_esco(data)
if args.createcipher or args.all:
    print("##########Creating cipher query##########")
    data = Graph.create_cipher_graph(data)

data = ESCO.connect_esco(data)
