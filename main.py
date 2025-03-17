
import ESCO
import CheckStructure
import csvFile
import pdfFile
import argparse
import Files
import MergeGraphs
import Startup
import Graph

necessary_folders = [
    './src/Cache',
    './src/ESCO',
    './src/Modules',
    './src/Output'
]



parser = argparse.ArgumentParser(description='pdf to graph')
parser.add_argument('--escodb', action='store_true', help='read esco csv and write to db')
parser.add_argument('--extractpdf', type=str, help='wandelt pdf in json um. example: --extractpdf=LLM_Angaben.pdf')
parser.add_argument('--escolabel', action='store_true', help='read ESCO-DB and extract preferred label and description')
parser.add_argument('--structure', action='store_true', help='check graph structure')
parser.add_argument('--all', action='store_true', help='all flags')
parser.add_argument('--config', type=str, help='name of the config file')
parser.add_argument('--merge', action='store_true', help='merge graphs')
parser.add_argument('--folderstructure', action='store_true', help='creates the folder structure of the project')
parser.add_argument('--connectesco', action='store_true', help='connect esco with skills in graph')
parser.add_argument('--createcipher', action='store_true', help='create cipher query')
parser.add_argument('--createjsongraph', action='store_true', help='create json graph from pdf json')

args = parser.parse_args()

if args.config:
    Files.CONFIG = args.config

if args.folderstructure or args.all:
    Startup.folder_structure(necessary_folders)
if args.escodb or args.all:
    csvFile.csv_to_db()
if args.extractpdf or args.all:
    pdfFile.extract_pdf(args.extractpdf)
if args.createjsongraph or args.all:
    Graph.create_json_graph()
if args.escolabel or args.all:
    csvFile.export_preferred_label()
if args.merge or args.all:
    MergeGraphs.merge()
if args.connectesco or args.all:
    ESCO.connect_esco()
if args.createcipher or args.all:
    Graph.create_cipher()
if args.structure or args.all:
    CheckStructure.check_structure()