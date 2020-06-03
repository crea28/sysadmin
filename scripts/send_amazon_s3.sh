#!/bin/bash 
# send_amazon_s3.sh
#######
# Author : Crea28.fr
# send files on amazon s3 bucket
# Version 1.1
# Notes : if file is greater than 5Go, please, use split -n x [files] to send
#######



LOG_FILE="" 
BACKUP_DIR="" 
DATE_HOUR=$(date "+%F-%Hh%M") 

function sends3 { 
  file=$1 
  bucket="" #to_FILL 
  resource="/${bucket}/${file}" 
  contentType="application/x-compressed-tar" 
  dateValue=`date -R` 
  stringToSign="PUT\n\n${contentType}\n${dateValue}\n${resource}" 
  s3Key= 
  s3Secret= 
  signature=`echo -en ${stringToSign} | openssl sha1 -hmac ${s3Secret} -binary | base64` 

  curl -X PUT -T "${file}" \ 
   -H "Host: ${bucket}.s3.amazonaws.com" \ 
   -H "Date: ${dateValue}" \ 
   -H "Content-Type: ${contentType}" \ 
   -H "Authorization: AWS ${s3Key}:${signature}" \ 
   https://${bucket}.s3.amazonaws.com/${file} 
} 

sends3 $1 

exit 1
