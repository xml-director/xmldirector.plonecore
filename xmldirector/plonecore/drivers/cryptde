#!/bin/bash
# cryptde - a script to decrypt files using openssl

FNAME=$1

if [[ -z "$FNAME" ]]; then
    echo "cryptde <name of file>"
    echo "  - cryptde is a script to decrypt des3 encrypted files"
    exit;
fi

openssl des3 -d -salt -in "$FNAME" -out "${FNAME%.[^.]*}"
