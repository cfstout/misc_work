

##!/usr/bin/env python

orig_logs = open('/Users/clayton.stout/BazaarVoice/SQLDebug.txt','r')
metrics = open('/Users/clayton.stout/BazaarVoice/metrics1.txt', 'w')
tables = open('/Users/clayton.stout/BazaarVoice/tables1.txt','w')

metrics_list = {}
for line in orig_logs:
    next_is_table=False
    for word in line.split():
        #print(word)
        if next_is_table:
            #print("writing" + word)
            tables.write('from '+word+'\n')
            if word in metrics_list:
                metrics_list[word]=metrics_list[word]+1
            else:
                metrics_list[word]=1
            next_is_table=False
        if word=='from':
            next_is_table=True

for table in sorted(metrics_list, key=metrics_list.get, reverse=True):
    metrics.write("Table: "+table+", num calls: "+str(metrics_list[table])+"\n")

metrics.close()
tables.close()

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
    p.add_argument('-l', '--list', dest='clusters', default='false', choices=['true','false'],
                   help='List the queries for the provided filter. Default is: do not list')

    options = p.parse_args()
