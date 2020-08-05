#!/bin/bash
# check_cpu.sh

# Exit codes
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3

# Variables
CRIT="90"
WARN="80"

CPU_USAGE="$(vmstat 1 2|tail -1)"
CPU_USER="$(echo ${CPU_USAGE} | awk '{print $13}')"
CPU_SYSTEM="$(echo ${CPU_USAGE} | awk '{print $14}')"
CPU_IDLE="$(echo ${CPU_USAGE} | awk '{print $15}')"
CPU_IOWAIT="$(echo ${CPU_USAGE} | awk '{print $16}')"
CPU_ST="$(echo ${CPU_USAGE} | awk '{print $17}')"

if [[ ${CPU_USER} -gt ${CRIT} || ${CPU_SYSTEM} -gt ${CRIT} || ${CPU_IOWAIT} -gt ${CRIT} || ${CPU_ST} -gt ${CRIT} ]]
then
	echo "CPU Usage is critical (u=${CPU_USER},sys${CPU_SYSTEM},i=${CPU_IDLE},io=${CPU_IOWAIT},st=${CPU_ST}) | user=${CPU_USER}, system=${CPU_SYSTEM}, idle=${CPU_IDLE}, iowait=${CPU_IOWAIT}, st=${CPU_ST}"
  exit ${STATE_CRITICAL};
elif [[ ${CPU_USER} -gt ${WARN} || ${CPU_SYSTEM} -gt ${WARN} || ${CPU_IOWAIT} -gt ${WARN} || ${CPU_ST} -gt ${WARN} ]]
then
  echo "CPU Usage is warning (u=${CPU_USER},sys${CPU_SYSTEM},i=${CPU_IDLE},io=${CPU_IOWAIT},st=${CPU_ST})| user=${CPU_USER}, system=${CPU_SYSTEM}, idle=${CPU_IDLE}, iowait=${CPU_IOWAIT}, st=${CPU_ST}"
  exit ${STATE_WARNING};
else
  echo "CPU Usage is ok (u=${CPU_USER},sys${CPU_SYSTEM},i=${CPU_IDLE},io=${CPU_IOWAIT},st=${CPU_ST})| user=${CPU_USER}, system=${CPU_SYSTEM}, idle=${CPU_IDLE}, iowait=${CPU_IOWAIT}, st=${CPU_ST}"
  exit ${STATE_OK};
fi

exit ${STATE_UNKNOWN};
