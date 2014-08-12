#!/usr/bin/env python
import json

try:
    import argparse
except ImportError, e:
    print e, '\nYour system has not module required.\n' \
             'To install required module please use:\n' \
             'easy_install module or pip install module'
    exit()


def contains(base_string, term_list):
    for term in term_list.split(" "):
        if not term in base_string:
            return False
    return True


# Assume standard log4j output.
# txt file containing info, warning, and debug statements
# We intentionally pull out the debugging es queries if they exist
def to_json(filename, start_line_number):
    json_string = ''
    with open(str(filename).strip("\'[]"), 'r') as file_reader:
        # start at message body
        cur_line = start_line_number + 1
        # find start of the query
        file_lines = file_reader.readlines()
        while not ("query" in file_lines[cur_line]):
            cur_line += 1
        #now we have the start of the query.
        #parse through. +1 for {
        # -1 for } we have finished when == 0
        depth = 1
        json_string += file_lines[cur_line].strip(" \n")
        cur_line += 1
        while depth > 0:
            line = file_lines[cur_line]
            if "{" in line:
                depth += 1
            if "}" in line:
                depth -= 1
                #handle edge case of trailing comma
                if depth == 0:
                    json_string += "}"
                    break
            json_string += line.strip(" \n")
            cur_line += 1

        return json.loads("{"+json_string+"}")


# recursive search to find key in json
def recursive_search(json_node, field):
    return_list = []
    if type(json_node) is dict:
        for json_key in json_node:
            if type(json_node[json_key]) in (list, dict):
                return_list += recursive_search(json_node[json_key], field)
            elif json_key == field:
                return json_node[json_key]
    elif type(json_node) is list:
        for item in json_node:
            if type(item) in (list, dict):
                return_list += recursive_search(item, field)
    return return_list


def parse_file(filename):
    json_list_map_by_table = {}
    with open(str(filename).strip("\'[]"), 'r') as file_reader:
        for line_num, line in enumerate(file_reader):
            next_is_table = False
            for word in line.split(" "):
                if next_is_table:
                    # Add 1 to line number because zero indexing
                    if word in json_list_map_by_table:
                        json_list_map_by_table[word].add(to_json(filename, line_num + 1))
                    else:
                        json_list_map_by_table[word] = [to_json(filename, line_num + 1)]
                    next_is_table = False
                if "SearchIndexQueryService" in word:
                    next_is_table = True

    return json_list_map_by_table


def print_tables(json_map, table_filter, list_bool, field):
    for table in json_map.keys():
        if contains(table, table_filter):
            print table + "    " + str(len(json_map.get(table)))

    if list_bool:
        for table in json_map.keys():
            if contains(table, table_filter):
                print table + "    " + len(json_map.get(table))
                for json_obj in json_map.get(table):
                    if len(field) > 0:
                        print("Filtered JSON")
                        for subset in recursive_search(json_obj, field):
                            print json.dumps(subset, separators=(',', ':'), indent=4)
                    else:
                        print json.dumps(json_obj, separators=(',', ':'), indent=4)


def start_interactive(json_map):
    print ("Interactive mode: 'TableFilter' filter_text to search through tables, " +
           "'Expand' to expand the filtered table, \n" +
           "'Field' field to only expand a particular field, 'Restart' to restart, 'Quit' to quit \n")

    filter_text = ''
    expand = False
    field = ''
    while True:
        user_command = raw_input('Selection? (TableFilter, Expand, Field,Restart,Quit')
        if user_command.split(" ").get(0) == "TableFilter":
            filter_text += user_command.split(" ").get(1) + " "
        elif user_command == "Expand":
            expand = True
        elif user_command.split(" ").get(0) == "Field":
            if not expand:
                print("Setting expand to true to do field matching")
            expand = True
            field = user_command.split(" ").get(1)
        elif user_command == "Restart":
            filter_text = ''
            expand = False
            continue
        elif user_command == "Quit":
            break
        else:
            print ("Sorry, command not recognized. Please try again.\n")
            continue

        print_tables(json_map, filter_text, expand, field)


def main():
    p = argparse.ArgumentParser(
        description='Tool to take in log4j out file with ES Debug logging and parse/classify the JSON queries',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='Usage examples:\n\n'
               'To interactively filter the logs in catalina.out:\n'
               '   ./ES_Log_parser -i catalina.out \n\n'
               'To filter by jcpenney tables queried in the logs from file /User/username/gitwork/logs/logfile.txt:\n'
               '   ./ES_Log_parser -t jcpenney /User/username/gitwork/logs/logfile.txt \n\n'
               'To see all queries to a catalog table from log file catalina.out: \n'
               '   ./ES_Log_parser -t catalog -l')

    p.add_argument('-i', '--interactive', dest='interactive', action="store_true",
                   help='Interactive Mode. Default is %(default)s')
    p.add_argument('-t', '--table', dest='table', default=':',
                   help='Table filter param. Default is %(default)s')
    p.add_argument('-l', '--list', dest='list', action="store_true",
                   help='List the queries for the provided filter. Default is: do not list')
    p.add_argument('filename', nargs=1,
                   help='The path to the log file to parse')

    options = p.parse_args()
    print options.interactive

    # Return a map of tables to a list of json queries to that table
    json_map = parse_file(options.filename)

    if options.interactive:
        print "true"
        start_interactive(json_map)
    else:
        print_tables(json_map, options.table, options.list, '')


if __name__ == "__main__":
    main()