#!/bin/bash

if [ $# -eq 0 ]
then
	echo "Használat: ./convert_for_dhcp bementi_fájl kimeneti_fájl\n";
exit;
fi

INPUT_FILE=$1;
OUTPUT_FILE=$2;
echo "Bemeneti fájl: "  $INPUT_FILE;
echo "Kimeneti fájl: "  $OUTPUT_FILE;


while read -r a b c
do
	if [ ${#a} -lt 1 ]
	then
		continue;
	fi
		echo "host "$a"{"
		echo "    hardware ethernet "$b";"
		echo "    fixed-address "$c";"
		echo "}"
		echo ""
done < $INPUT_FILE
