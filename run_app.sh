#!/bin/bash

# This loop is for multi-query. =w=
while true; do
    # To set the GUI. =w=
    echo "
          
            Start a new query for app.py. =w=
          
          
          
                    

            [-dr / --drop]
            [-tr / --truncate]
            [-f / --filepath FILEPATH]
            [-d / --database DATABASE]
            [-s / --start START NODE]
            [-e / --end [END NODES]]
            [-x / --exclude [EXCLUDED NODES]]
            [-i / --include [INCLUDED NODES]]
            [-a / --add [ADDED NODES]]
            [-c / --cost [COST CHANGES]]
            
            
            "


    # To enable the user input. =w=
    read -p "Please enter the arguments or using ctrl+c to quit: " args

    # Important input configure line. =w=
    # You can set predefine value, such as python app.py -d test_case. Then add the input field.
    py app.py $args

    # To enable the user see the output. =w=
    read -p "Type any key to go next round"
done