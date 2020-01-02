#!/bin/sh

#
#       Requirements:
#               - lm-sensors After the installation please run the sensor-detect command!
#               - hddtemp
#               - sendmail
#               - fdisk
#
#       Author: Gabor Kiss, University of Debrecen, HU
#       Mail: kiss.gabor@it.unideb.hu
#       Date: 2013.09.02
#       Last modify: 2013.09.04

SLEEP_TIME=2;
WAIT_FOR_ERROR_PREVENTION=10; # sec
START_DATE=$(date);
DATA_FILE_STORE="/root/";
DATA_FILE_PREFIX="";
DATA_FILE_INFIX=$(date +"%Y-%m-%d");
DATA_FILE_POSTFIX=".sensor";

TMP_FILE="/tmp/sensors.tmp";
DATA_FILE=${DATA_FILE_STORE}${DATA_FILE_PREFIX}${DATA_FILE_INFIX}${DATA_FILE_POSTFIX};

#
#                               Levels
#
INFORMATION=0;				# Only e-mail
WARNING=1;					# Only e-mail
CRITICAL=2;					# Mail + outer action
FATAL=3;					# Mail + auto pre-defined action

#################################################################################
#                               CPU settings                                    #
#################################################################################
CPU_NORMAL_TEMP=50;             # Normál mûködés felsõ korlátja; csak információ
CPU_HIGH_TEMP=65;               # Magas hõmérséklet; jelzés levélben
CPU_CRITICAL_TEMP=80;           # Kritikus hõmérséklet, de még mûködõképes; jelzés levélben: hõmérséklet és folyamatok
CPU_FATAL_TEMP=90;              # Végzetes hõmérséklet; beavatkozás => vészleállás kezdeményezése

#
#       Motherboard
#
MB_NORMAL_TEMP=55;
MB_HIGH_TEMP=65;
MB_CRITICAL_TEMP=75;
MB_FATAL_TEMP=85;

#################################################################################
#                               HDD settings                                    #
#################################################################################

HDD_NORMAL_TEMP=50;
HDD_HIGH_TEMP=65;
HDD_CRITICAL_TEMP=75;
HDD_FATAL_TEMP=85;

HDD_DRIVES=$(fdisk -l | grep 'lemez\|Disk'| awk '{print $1}');

#################################################################################
#                               Variables                                       #
#################################################################################

FAN_SPEED=0;
MB_TEMP=0;
CPU_TEMP=0;
CORE_TEMP="";
HDD_TEMP="";
MAX_HDD_TEMP=0;

#################################################################################
#                               END settings                                    #
#################################################################################

function create_data_file()
{
        touch ${DATA_FILE};
        echo "Adatfájl létrehozva: ${DATA_FILE} ";
        echo "Idõbélyeg;Szenzor név;Érték;" > ${DATA_FILE};
}

function read_CPU_sensors()
{
        sensors > $TMP_FILE;

        # Ventillátor sebesség olvasása
        cat ${TMP_FILE} | grep ^"CPU FAN" | awk '{print strftime("%Y.%m.%d %H-%M-%S") ";\t" $1 " " $2 " " $3 ";\t" $4 ";" }' | sed -e 's/°C//g' -e 's/://g' # >> ${DATA_FILE};

        # Processzor és alaplap hõmérséklet olvasása
        cat ${TMP_FILE} | grep "Temperature"|awk '{print strftime("%Y.%m.%d %H-%M-%S") ";\t" $1 " " $2 ";\t" $3 ";"}' | sed -e 's/°C//g' -e 's/://g' # >> ${DATA_FILE};

        # Processzor magok hõmérséklete
        cat ${TMP_FILE} | grep "Core"|awk '{print strftime("%Y.%m.%d %H-%M-%S") ";\t" $1 " " $2 ";\t" $3 ";" }'| sed -e 's/°C//g' -e 's/://g' # >> ${DATA_FILE};

        # Processzor hõmérséklete
        CPU_TEMP=$(cat ${TMP_FILE} | grep ^"CPU Temperature" | awk '{print $3}'|sed -e 's/°C//g' -e 's/+//g');

        # Alaplap hõmérséklete
        MB_TEMP=$(cat ${TMP_FILE} | grep ^"MB Temperature" | awk '{print $3}'|sed -e 's/°C//g' -e 's/+//g');

        # CPU mag[ok] hõmérséklete
        CORE_TEMP=$(cat ${TMP_FILE} | grep ^"Core" | awk '{print $3}'|sed -e 's/°C//g' -e 's/+//g');

        # Venti sebessége [RPM]
        FAN_SPEED=$(cat ${TMP_FILE} | grep ^"CPU FAN" | awk '{print $4}');

}

function read_HDD_sensors()
{
        local counter=0;
        local sum_temp=0;
        local max_temp=0;

        for HDD in $HDD_DRIVES
        do
                echo "HDD: "$HDD;
                HDD_TEMP=$(hddtemp ${HDD} | awk '{print $4}' | sed -e 's/°C//g' -e 's/+//g' -e 's/://g');

                if [[ $max_temp -lt $HDD_TEMP  ]]
                then
                    max_temp=$HDD_TEMP;
                fi

                counter=$(( $counter + 1 ));
                echo $counter;
                echo ${HDD_TEMP};
        done

        MAX_HDD_TEMP=$max_temp;
}

function error_prevention_mechanism()
{
    echo "Prevention is started!";
}

function information_action()
{
    echo "Information";
}

function warning_action()
{
    echo "Warning";
}

function critical_action()
{
    echo "Critical";
}

function fatal_action()
{
    echo "Fatal";
}

function check_sensors_state()
{
    result=0;

}

function main()
{
	counter=0;
    mail_content="";
    mail_important_content="";
    warning_level=$INFORMATION;

        if [ ! -f $DATA_FILE ]
        then
                create_data_file;
        fi

        read_CPU_sensors;
        read_HDD_sensors;

        check_sensors_state result;
        echo $result;

		#
		#	Check CPU
		#
        if [[ $CPU_TEMP -le $CPU_NORMAL_TEMP ]]
        then
            mail_content .= "CPU is really cold: ${CPU_TEMP}";
        else if [ $CPU_TEMP -gt $CPU_NORMAL_TEMP ] && [ $CPU_TEMP -le $CPU_HIGH_TEMP ]
        then
            mail_content .= "CPU temperature is normal: ${CPU_TEMP}";
        else if [ $CPU_TEMP -gt $CPU_HIGH_TEMP ] && [ $CPU_TEMP -le $CPU_CRITICAL_TEMP ]
        then
            mail_important_content .= "CPU temperature is HIGH ( ${CPU_TEMP} )! Please check running jobs!";
			
			if [ $warning_level -lt $WARNING ]
			then
				warning_level=$WARNING;
			fi
            
        else if [ $CPU_TEMP -gt $CPU_CRITICAL_TEMP ] && [ $CPU_TEMP -le $CPU_FATAL_TEMP ]
        then
            mail_important_content .= "CPU temperature is CRITICAL( ${CPU_TEMP} )! Please check running jobs!";
            
			if [ $warning_level -lt $CRITICAL ]
			then
				warning_level=$CRITICAL;
			fi
        else if [ $CPU_TEMP -gt $CPU_FATAL_TEMP ]
        then
            mail_important_content .= "CPU temperature is VERY HIGH ( ${CPU_TEMP} ), I will be execute your pre-defined ERROR PREVENTION mechanism in ${WAIT_FOR_ERROR_PREVENTION} second!";
            			
			if [ $warning_level -lt $FATAL ]
			then
				warning_level=$FATAL;
			fi
        fi

		#
		#	Check Motherboard
		#
        if [[ $MB_TEMP -le $MB_NORMAL_TEMP ]]
        then
            mail_content .= "Motherboard is really cold: ${MB_TEMP}";
        else if [ $MB_TEMP -gt $MB_NORMAL_TEMP ] && [ $MB_TEMP -le $MB_HIGH_TEMP ]
        then
            mail_content .= "Motherboard temperature is normal: ${MB_TEMP}";
        else if [ $MB_TEMP -gt $MB_HIGH_TEMP ] && [ $MB_TEMP -le $MB_CRITICAL_TEMP ]
        then
            mail_important_content .= "Motherboard temperature is HIGH ( ${MB_TEMP} )! Please check running jobs!";
            
			if [ $warning_level -lt $WARNING ]
			then
				warning_level=$WARNING;
			fi
        else if [ $MB_TEMP -gt $MB_CRITICAL_TEMP ] && [ $MB_TEMP -le $MB_FATAL_TEMP ]
        then
            mail_important_content .= "Motherboard temperature is CRITICAL( ${MB_TEMP} )! Please check running jobs!";
            if [ $warning_level -lt $CRITICAL ]
			then
				warning_level=$CRITICAL;
			fi
        else if [ $MB_TEMP -gt $MB_FATAL_TEMP ]
        then
            mail_important_content .= "Motherboard temperature is VERY HIGH ( ${MB_TEMP} ), I will be execute your defined ERROR PREVENTION mechanism in ${WAIT_FOR_ERROR_PREVENTION} second!";
            if [ $warning_level -lt $FATAL ]
			then
				warning_level=$FATAL;
			fi
        fi


		#
		#	Check CPU Cores
		#
		for $CORE in $CORE_TEMP
        do
			counter=$(( $counter + 1 ));
			if [[ $CORE -le $CPU_NORMAL_TEMP ]]
			then
				mail_content .= "CPU CORE ${counter} is really cold: ${CORE}";
			else if [ $CORE -gt $CPU_NORMAL_TEMP ] && [ $CORE -le $CPU_HIGH_TEMP ]
			then
				mail_content .= "CPU CORE ${counter} temperature is normal: ${CORE}";
			else if [ $CORE -gt $CPU_HIGH_TEMP ] && [ $CORE -le $CPU_CRITICAL_TEMP ]
			then
				mail_important_content .= "CPU CORE ${counter} temperature is HIGH ( ${CORE} )! Please check running jobs!";
				if [ $warning_level -lt $WARNING ]
				then
					warning_level=$WARNING;
				fi
			else if [ $CORE -gt $CPU_CRITICAL_TEMP ] && [ $CORE -le $CPU_FATAL_TEMP ]
			then
				mail_important_content .= "CPU CORE ${counter} temperature is CRITICAL( ${CORE} )! Please check running jobs!";
				if [ $warning_level -lt $CRITICAL ]
				then
					warning_level=$CRITICAL;
				fi
			else if [ $CORE -gt $CPU_FATAL_TEMP ]
			then
				mail_important_content .= "CPU CORE ${counter} temperature is VERY HIGH ( ${CORE} ), I will be execute your defined ERROR PREVENTION mechanism in ${WAIT_FOR_ERROR_PREVENTION} second!";
				if [ $warning_level -lt $FATAL ]
				then
					warning_level=$FATAL;
				fi
			fi
		done

		
		#
		#	Check HDD
		#
        if [[ $MAX_HDD_TEMP -le $CPU_NORMAL_TEMP ]]
        then
            mail_content .= "HDD is really cold: ${MAX_HDD_TEMP}";
        else if [ $MAX_HDD_TEMP -gt $HDD_NORMAL_TEMP ] && [ $MAX_HDD_TEMP -le $HDD_HIGH_TEMP ]
        then
            mail_content .= "HDD temperature is normal: ${MAX_HDD_TEMP}";
        else if [ $MAX_HDD_TEMP -gt $HDD_HIGH_TEMP ] && [ $MAX_HDD_TEMP -le $HDD_CRITICAL_TEMP ]
        then
            mail_important_content .= "HDD temperature is HIGH ( ${MAX_HDD_TEMP} )! Please check running jobs!";
            if [ $warning_level -lt $WARNING ]
				then
					warning_level=$WARNING;
				fi
        else if [ $MAX_HDD_TEMP -gt $HDD_CRITICAL_TEMP ] && [ $MAX_HDD_TEMP -le $HDD_FATAL_TEMP ]
        then
            mail_important_content .= "HDD temperature is CRITICAL( ${MAX_HDD_TEMP} )! Please check running jobs!";
            if [ $warning_level -lt $CRITICAL ]
				then
					warning_level=$CRITICAL;
				fi
        else if [ $MAX_HDD_TEMP -gt $HDD_FATAL_TEMP ]
        then
            mail_important_content .= "HDD temperature is VERY HIGH ( ${MAX_HDD_TEMP} ), I will be execute your defined ERROR PREVENTION mechanism in ${WAIT_FOR_ERROR_PREVENTION} second!";
            if [ $warning_level -lt $FATAL ]
				then
					warning_level=$FATAL;
				fi
        fi
		
		if [ $warning_level -lt $WARNING ]
		then
			# Information action, define here!!!!!!!!!!!!!!!!!!!!!!!!!
		else if [ $warning_level -ge $WARNING ] && [ $warning_level -lt $CRITICAL ]
			# Warning action, define here!!!!!!!!!!!!!!!!!!!!!!!!!			
		else if [ $warning_level -ge $CRITICAL ] && [ $warning_level -lt $FATAL ]
			# Critical action, define here!!!!!!!!!!!!!!!!!!!!!!!!!
		else if [ $warning_level -gt $FATAL ]
			# Fatal action, define here!!!!!!!!!!!!!!!!!!!!!!!!!
		fi

}

main;
