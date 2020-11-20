#!/bin/bash

###########################################################################################################################################
#  Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved                                                                  #
#                                                                                                                                          #
#  Licensed under the MIT No Attribution License (MIT-0) (the ‘License’). You may not use this file except in compliance                   #
#  with the License. A copy of the License is located at                                                                                   #
#                                                                                                                                          #
#      https://opensource.org/licenses/MIT-0                                                                                               #
#                                                                                                                                          #
#  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files        #
#  (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge,     #
#  publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.  #
#  THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF      #
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR #
#  ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH  # 
#  THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                                              #
############################################################################################################################################
#
# This assumes all of the OS-level configuration has been completed and git repo has already been cloned
#
# This script should be run from the repo's deployment directory
# cd deployment
# ./run-unit-tests.sh
#

# Get reference for all important folders
template_dir="$PWD"
source_dir="$template_dir/../source"

function clean_up {
  find . -maxdepth 1 -not -name "*.py" -not -name "requirements.txt" -not -name "package.json" -not -name "." -not -name "*.js" -not -name "*.ndjson" -not -name "*.yaml"| xargs -I {} rm -rf {}
}

function executeUnitTests {
  FUNCTION_NAME=$1
  DEPENDENCY=$2

  echo "------------------------------------------------------------------------------"
  echo "[Test] Services - $1"
  echo "------------------------------------------------------------------------------"

  cd $source_dir/$FUNCTION_NAME

  if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -t .
  fi

  if [[ -n "$DEPENDENCY" ]]; then
    pip install $DEPENDENCY
  fi
  
  python -m unittest
  clean_up
}

executeUnitTests getCurrentAddress
executeUnitTests getCoordsFromAddress
executeUnitTests cognitoPosConfirmation moto
executeUnitTests manageMessages
executeUnitTests sendMessage
