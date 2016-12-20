# deep-tools

Using the ClusterDB script
==========================

Master Setup
------------

Primary Master:
`clusterDb.py --server=1 --data=master1 --db=test`

Backup Master:
`clusterDb.py --server=4 --data=master2 --port=3309 --db=test`

Slave Setup
-----------
`clusterDb.py --server=2 --data=slave1 --port=3307 --slave --db=test
clusterDb.py --server=3 --data=slave2 --port=3308 --slave --db=test

change master to master_user='root',master_port=3306,master_host='localhost',master_log_file='mysql-bin.00000?',master_log_pos=<#>;`

CLI
---
`clusterDb.py --cli --data=slave1
clusterDb.py --cli --data=slave2
clusterDb.py --cli --data=master1
clusterDb.py --cli --data=master2`
