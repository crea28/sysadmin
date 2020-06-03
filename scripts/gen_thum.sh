#!/bin/bash
# gen_thumb.sh 

if [[ ! -d thumb ]]; then
	mkdir -p thumb
fi

for i in `ls *.{jpg,JPG,NEF,RAF} 2>/dev/null`
do
	test=`convert ${i} -format "%[fx:(w/h>1)?1:0]" info:`
	if [ $test -eq 1 ]; then
		# landscape
		convert ${i} -resize 800x thumb/thumb_${i}
	else
		# portrait
		convert ${i} -resize x800 thumb/thumb_${i}
	fi
done

