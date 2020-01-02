#!/bin/bash

echo "Starting to process the file"

DEVICE_NAME=""
PREV_DEVICE_NAME=""
DEVICE_IP=""
NO_OF_SFP10GB=0
#SFP-10GBase
NO_OF_GLC_SX_MMD=0
#1000BaseSX
NO_OF_GLC_LH=0
#1000BaseLH
NO_OF_GLC_T=0
#1000BaseT
NO_OF_CDP_NEIG=0
	
	echo -e "DEVICE_NAME\tNO_OF_SFP10GB\tNO_OF_GLC_SX_MMD\tNO_OF_GLC_LH\tNO_OF_GLC_T\tNO_OF_CDP_NEIG"
	
while IFS='' read -r lines ; do
# `cat results.log`

       # echo "$lines"
       #  echo "$lines" | grep -v "connected\|dhle-r" | grep "dhle-sw\|/*>\|NAME:\|PID:\|cdp\|Device"
       # echo $lines | grep "Domain\|Operating" | grep -v "term\|.exit\|.connected" | awk -F'[:]' '{print $2 }'
	   
	   FILTERED_LINE=$( echo "$lines" | grep -v "connected\|dhle-r" | grep "dhle-sw\|/*>\|NAME:\|PID:\|cdp\|Device" )
	   
	   
	   if [[ $FILTERED_LINE ]]; then
					# get hostname
					#echo " LINE:	$FILTERED_LINE "
					TEMP_FILTERED_LINE=$(echo "$FILTERED_LINE" | grep "^dhle-sw\(.*\)>")
						if [[ $TEMP_FILTERED_LINE ]]; then
					#		echo -e "\t Set device name\t$TEMP_FILTERED_LINE"
							DEVICE_NAME=$(echo "$TEMP_FILTERED_LINE" | grep "/*>"  | awk -F'[>]' '{print $1 }')
					
							if [[ "$DEVICE_NAME" != "$PREV_DEVICE_NAME" ]]; then
							
					#			echo -e "\t\tDevice name does not match\t'$DEVICE_NAME'\t'$PREV_DEVICE_NAME'\t"
								PREV_DEVICE_NAME=$(echo "$DEVICE_NAME")
								
								echo -e "$DEVICE_NAME \t $NO_OF_SFP10GB \t $NO_OF_GLC_SX_MMD \t $NO_OF_GLC_LH \t $NO_OF_GLC_T \t $NO_OF_CDP_NEIG"
								DEVICE_IP=""
								NO_OF_SFP10GB=0
								NO_OF_GLC_SX_MMD=0
								NO_OF_GLC_LH=0
								NO_OF_GLC_T=0
								NO_OF_CDP_NEIG=0
					#			echo -e "Continue 1"
								
							#else
							#	echo -e "\t\tDevice name match\t'$DEVICE_NAME'\t'$PREV_DEVICE_NAME'\t"
					#
							fi
							#echo -e "Continue 1.2"
							continue
						fi
				# count 10G SFP's
					TEMP_FILTERED_LINE=$(echo "$FILTERED_LINE" | grep "10GBase-LR\|10Gbase-LR")
					if [[ $TEMP_FILTERED_LINE ]]; then
						NO_OF_SFP10GB=$[$NO_OF_SFP10GB +1]
						#echo "Found a 10GB SFP"
						#echo -e "Continue 2"
						continue
					fi
				# count 1000BaseSX
					TEMP_FILTERED_LINE=$(echo "$FILTERED_LINE" | grep "1000BaseSX")
					if [[ $TEMP_FILTERED_LINE ]]; then
						NO_OF_GLC_SX_MMD=$[$NO_OF_GLC_SX_MMD +1]
						#echo "Found a 1GB SX SFP"
						#echo -e "Continue 3"
						continue
					fi
				# count 1000BaseLH
					TEMP_FILTERED_LINE=$(echo "$FILTERED_LINE" | grep "1000BaseLH\|1000BaseLX")
					if [[ $TEMP_FILTERED_LINE ]]; then
						NO_OF_GLC_LH=$[$NO_OF_GLC_LH +1]
						#echo "Found a 1GB LH SFP"
						#echo -e "Continue 4"
						continue
					fi
				# count 1000BaseT
					TEMP_FILTERED_LINE=$(echo "$FILTERED_LINE" | grep "1000BaseT")
					if [[ $TEMP_FILTERED_LINE ]]; then
						NO_OF_GLC_T=$[$NO_OF_GLC_T +1]
						#echo "Found a 1GB GLC-T SFP"
						#echo -e "Continue 5"
						continue
					fi
					
				# count CDP neigh
					TEMP_FILTERED_LINE=$(echo "$FILTERED_LINE" | grep "dhle-sw")
					if [[ $TEMP_FILTERED_LINE ]]; then
						NO_OF_CDP_NEIG=$[$NO_OF_CDP_NEIG +1]
						#echo "Found a CDP neigh $TEMP_FILTERED_LINE"
						#echo -e "Continue 6"
						continue
					fi
			
		fi

continue	   
	   if [[ -z "$(echo "$lines" | grep -v "connected" | grep "dhle-sw\|/*>\|NAME:\|PID:\|cdp\|Device")" ]]
	   then
			echo "$lines"
			#if [ -z "$(echo "$lines" | grep "ssh")" ]
			#then
			#	DEVICE_NAME=$(echo "$lines" | grep "ssh" | awk '{print $4}')
			#	echo "Device name: $DEVICE_NAME"
			#	echo "$lines"
			#fi
	   fi
	   

	   
# $lines | awk -F'[>:]' '{print $1}'
#echo $lines
done < "results.log"

echo -e "$DEVICE_NAME \t $NO_OF_SFP10GB \t $NO_OF_GLC_SX_MMD \t $NO_OF_GLC_LH \t $NO_OF_GLC_T \t $NO_OF_CDP_NEIG"
