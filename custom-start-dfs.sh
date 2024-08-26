!/bin/bash
/opt/hadoop-2.7.4/sbin/hadoop-daemon.sh start namenode
/opt/hadoop-2.7.4/sbin/hadoop-daemon.sh start datanode
/opt/hadoop-2.7.4/sbin/hadoop-daemon.sh start secondarynamenode
tail -f /dev/null
