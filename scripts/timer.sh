#!/bin/bash
# timer.sh 
# apt-get update && apt-get install pico2wave
# test script

display_usage() {
  echo
  echo "Usage: $0"
  echo
  echo " -m, --minute(s)"
  echo " -s, --second(s)"
  echo
}

function min2Sec () {
	minutes=$1
	seconds=$(($1*60))

	if [ "${minutes}" -eq 0 ] || [ "${minutes}" -eq 1 ]; then
	 	text="minute";
	else
		text="minutes";
	fi

	echo "Timer for $1 ${text}"

	while [ $seconds -gt 0 ]; do
        printf "\r\033[KWaiting %.d seconds" $((seconds--))
	    sleep 1
	done

	sendNotif "Temps écoulé : $1 ${text} !"
}


function inSecs () {
	seconds=$1

	if [ "${seconds}" -eq 0 ] || [ "${seconds}" -eq 1 ]; then
	 	text="seconde";
	else
		text="secondes";
	fi

	echo "Timer for $1 ${text}"

	while [ $seconds -gt 0 ]; do
        printf "\r\033[KWaiting %.d seconds" $((seconds--))
	    sleep 1
	done

	sendNotif "Temps écoulé : $1 ${text} !"
}

function sendNotif () {

	notify-send -i face-wink test "$1"
	pico2wave -l fr-FR -w test.wav "$1";
	play test.wav
	rm -rf test.wav

}

if [[ -z "$1" ]]; then
	echo "argument missing !"
	display_usage
else
	case $1 in
    -m)
	  shift;
      min2Sec $1
      ;;
    -s)
	  shift;
	  inSecs $1
      ;;
    *)
      echo "Unknown argument: ${argument}"
      display_usage
      ;;
  esac
fi
