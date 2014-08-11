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
