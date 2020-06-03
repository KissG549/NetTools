#!/bin/bash

if [ $# -eq 0 ]
then
	echo "Usage: ./convert_for_dhcp input_file output_file\n";
exit;
fi

INPUT_FILE=$1;
OUTPUT_FILE=$2;
echo "Input filename: "  $INPUT_FILE;
echo "Output filename: "  $OUTPUT_FILE;


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
