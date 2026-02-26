#!/bin/bash

dir=$1

# delete directories 1st
find $dir -name '*aid2e*' -type d -exec rm -r "{}" \;

# delete files 2nd
find $dir -name '*aid2e*' -delete
