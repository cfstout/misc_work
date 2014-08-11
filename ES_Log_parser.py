#!/usr/bin/env python

import fileinput
import json

try:
    import argparse
except ImportError, e:
    print e, '\nYour system has not module required.\n' \
             'To install required module please use:\n' \
             'easy_install module or pip install module'
    exit()

#Assume standard log4j output.
#txt file containing info, warning, and debug statements
#We intentionally pull out the debugging es queries if they exist
def toJson(filename, start_line_number):
    json_string = ''
    with open(filename, 'r') as file:
        #start at message body
        cur_line = start_line_number+1
        #find start of the query
        while not(filename.get(cur_line).contain("query")):
            cur_line += 1
        #now we have the start of the query.
        #parse through. +1 for {
        # -1 for } we have finished when == 0
        depth = 1
        json_string.append(filename.get(cur_line))
        cur_line+=1
        while depth > 0:
            line = filename.get(cur_line)
            if line.contains("{"):
                depth += 1
            if line.contains("}"):
                depth -= 1
            json_string.append(line)

        return json.loads(json_string)


def parse_file(filename):
    json_list_map_by_table = {}
    for line in fileinput.input(filename):
        next_is_table=False
        for word in line.split():
            if next_is_table:
                json_list_map_by_table[word].add(toJson(filename, fileinput.filelineno()))
                next_is_table=False
            if word.contains('SearchIndexQueryService'):
                next_is_table=True


def main():
    p = argparse.ArgumentParser(description = 'Tool to take in log4j out file with ES Debug logging and parse/classify the JSON queries',
                                formatter_class = argparse.RawTextHelpFormatter,
                                epilog='Usage examples:\n\n' \
                                       'To interactively filter the logs in catalina.out:\n' \
                                       '   ./ES_Log_parser -i catalina.out \n\n' \
                                       'To filter by jcpenney tables queried in the logs from file /User/username/gitwork/logs/logfile.txt:\n' \
                                       '   ./ES_Log_parser -t jcpenney /User/username/gitwork/logs/logfile.txt \n\n' \
                                       'To see all queries to a catalog table from log file catalina.out: \n' \
                                       '   ./ES_Log_parser -t catalog -l')

    p.add_argument('-i', '--interactive', dest='interactive', default='false', choices=['true','false'],
                   help='Interactive Mode. Default is %(default)s')
    p.add_argument('-t', '--table', dest='table', default='',
                   help='Table filter param. Default is %(default)s')
    p.add_argument('-l', '--list', dest='list', default='false', choices=['true','false'],
                   help='List the queries for the provided filter. Default is: do not list')
    p.add_argument('filename', dest='filename', nargs=1, type=str,
                    help='The path to the log file to parse')

    options = p.parse_args()

    #Return a map of tables to a list of json queries to that table
    json_map = parse_file(options.filename)

