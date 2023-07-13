#!/bin/bash
# Name : watermark.sh
# Description : Create a thumbnail with a watermark from a HD picture. Don't forget to create watermark .png pictures 
# Safety first : Always do it on working copy !
# Author comment : Maybe not the most beautiful script but it's working !
 
# Variables
watermarkFolder="~/Pictures"
count=1

# Asking for renaming files
echo -n "Name of file ? "
read new_basename

# Renaming the files
## Browse all the files in the folder
for file in `ls`; do
    # Check if this is a file or not
    if [ -f "$file" ]; then
        # Get the file extension
        extension="${file##*.}"
        # Create the new name
        new_name="$new_basename-$(printf "%03d" $count).$extension"
        # Rename the file
        mv "$file" "$new_name"
        # Increment the counter
        count=$((count + 1))
    fi
done

# Creating thumbnail
## Create a thumb directory
if [[ ! -d thumb ]]; then
	mkdir -p thumb
fi
## Check the orientation
for thumb in `ls *.{jpg,JPG} 2>/dev/null`
do
	checkFormat=`convert ${thumb} -format "%[fx:(w/h>1)?1:0]" info:`
	if [ $checkFormat -eq 1 ]; then
		# landscape
		convert ${thumb} -resize 800x thumb/${thumb}
	else
		# portrait
		convert ${thumb} -resize x800 thumb/${thumb}
	fi
done

# Adding the watermark
## Browse all the files in the folder
cd thumb
for file in `ls *`; do
    # Check if the file is a picture
    if [[ -f "$file" && "$file" =~ \.(jpg|jpeg|png|gif)$ ]]; then
        # Apply the watermark to the picture with transparency and positioning
        orientation=$(identify -format "%[EXIF:Orientation]" "$file")
        case $orientation in
            "3")
                # Absolute or relative path to the watermark file
                watermarkPath="${watermarkFolder}/watermark-landscape-reverse.png"
                # Landscape format but held upside down like a Smartphone
                composite -dissolve 65 -gravity NorthEast -geometry +20+20 "$watermarkPath" "$file" "${file//.jpg}.jpg"
                ;;
            "6")
                # Absolute or relative path to the watermark file
                watermarkPath="${watermarkFolder}/watermark-portrait.png"
                # OK portrait format
                composite -dissolve 100 -gravity SouthEast -geometry +20+20 "$watermarkPath" "$file" "${file//.jpg}.jpg"
                ;;
            "1")
                # Absolute or relative path to the watermark file
                watermarkPath="${watermarkFolder}/watermark-landscape.png"
                # OK landscape format
                composite -dissolve 80 -gravity SouthWest -geometry +20+20 "$watermarkPath" "$file" "${file//.jpg}.jpg"
                ;;
            *)
                # By default
                # Absolute or relative path to the watermark file
                watermarkPath="${watermarkFolder}/watermak.png"
                composite -dissolve 45 -gravity SouthWest -geometry +20+20 "$watermarkPath" "$file" "${file//.jpg}.jpg"
                ;;
        esac         
    fi 
done