#!/bin/bash
# crypten - a script to encrypt files using openssl

FNAME=$1

if [[ -z "$FNAME" ]]; then
    echo "crypten <name of file>"
    echo "  - crypten is a script to encrypt files using des3"
    exit;
fi

openssl des3 -salt -in "$FNAME" -out "$FNAME.des3"
