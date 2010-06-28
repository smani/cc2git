#!/bin/bash
LOG=log.txt
SLEEP=600

echo >> $LOG
echo -n "Date," >> $LOG
date >> $LOG
echo "Sleep,$SLEEP" >> $LOG
while [ 1 ]
do
    ps ax >> $LOG
	sleep $SLEEP
done

