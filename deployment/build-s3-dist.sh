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
# ./build-s3-dist.sh source-bucket-base-name solution-name version-code
#
# Paramenters:
#  - source-bucket-base-name: Name for the S3 bucket location where the template will source the Lambda
#    code from. The template will append '-[region_name]' to this bucket name.
#    For example: ./build-s3-dist.sh solutions my-solution v1.0.0
#    The template will then expect the source code to be located in the solutions-[region_name] bucket
#
#  - solution-name: name of the solution for consistency
#
#  - version-code: version of the package

######
### IF YOU WANT TO SKIP BUILDING THE FUNCTIONS ### 
### ONLY USE IF DEBUGGING THE CLOUDFORMATION STACKS ####
######
skip="false"

# Check to see if input has been provided:
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "Please provide the base source bucket name, trademark approved solution name and version where the lambda code will eventually reside."
    echo "For example: ./build-s3-dist.sh solutions trademarked-solution-name v1.0.0 template-bucket"
    exit 1
fi

# Get reference for all important folders
template_dir="$PWD"
template_dist_dir="$template_dir/global-s3-assets"
build_dist_dir="$template_dir/regional-s3-assets"
source_dir="$template_dir/../source"

echo "------------------------------------------------------------------------------"
echo "[Init] Clean old dist, node_modules and bower_components folders"
echo "------------------------------------------------------------------------------"
echo "rm -rf $template_dist_dir"
rm -rf $template_dist_dir
echo "mkdir -p $template_dist_dir"
mkdir -p $template_dist_dir
echo "rm -rf $build_dist_dir"
rm -rf $build_dist_dir
echo "mkdir -p $build_dist_dir"
mkdir -p $build_dist_dir

echo "------------------------------------------------------------------------------"
echo "[Packing] Templates"
echo "------------------------------------------------------------------------------"
echo "cp $template_dir/*.template $template_dist_dir/"
cp $template_dir/*.template $template_dist_dir/
echo "copy yaml templates and rename"
cp $template_dir/*.yaml $template_dist_dir/
cd $template_dist_dir
# Rename all *.yaml to *.template
for f in *.yaml; do 
    mv -- "$f" "${f%.yaml}.template"
done

cd ..
echo "Updating code source bucket in template with $1"
replace="s/%%BUCKET_NAME%%/$1/g"
echo "sed -i '' -e $replace $template_dist_dir/*.template"
sed -i '' -e $replace $template_dist_dir/*.template
replace="s/%%SOLUTION_NAME%%/$2/g"
echo "sed -i '' -e $replace $template_dist_dir/*.template"
sed -i '' -e $replace $template_dist_dir/*.template
replace="s/%%VERSION%%/$3/g"
echo "sed -i '' -e $replace $template_dist_dir/*.template"
sed -i '' -e $replace $template_dist_dir/*.template
replace="s/%%TEMPLATE_OUTPUT_BUCKET%%/$4/g"
echo "sed -i '' -e $replace $template_dist_dir/*.template"
sed -i '' -e $replace $template_dist_dir/*.template


# Modified by Paulo Aragao
echo "------------------------------------------------------------------------------"
echo "[Build] Building functions"
echo "------------------------------------------------------------------------------"
# ATTENTION # 
# must remove all files not required for the build
# or the Viperlight script will throw out a bunch of alerts/criticals

# Instructions:
# change FUNCTION_NAME to be exactly the *.zip file that your CFN template will use
# also make sure that directory you create under $source_dir has the same name as the FUNCTION_NAME
# copy/paste the one of the "blocks" below and just change the variable FUNCTION_NAME, the rest will work to build either a Node.JS or Python function
# for Python, make sure you have a "requirements.txt" in the function directory
# for Node.JS, make sure you have your package.json with the correct build, zip, etc, in it. 

# Helper functions
function is_python {
    if [ $(find . -maxdepth 1 -name "*.py" |wc -l |awk '{print $1}') -ne 0 ]; then
        true
    fi
}

function clean_up {
    find . -maxdepth 1 -not -name "*.py" -not -name "requirements.txt" -not -name "package.json" -not -name "package-lock.json" -not -name "." -not -name "*.js" -not -name "*.ndjson" -not -name "*.yaml"| xargs -I {} rm -rf {}
}

# a hack to skip building everything and just create the templates
if [[ $skip != "true" ]] ; then

echo "Building getCurrentAddress (from geofence-apis.template)"
FUNCTION_NAME="getCurrentAddress"
cd $source_dir/$FUNCTION_NAME
if is_python; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -t .
    fi
    zip -9r $FUNCTION_NAME.zip . -x test_getCurrentAddress.py
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
elif [ -f "package.json" ]; then
    if [ -f "package-lock.json" ]; then 
        rm -rf package-lock.json
    fi
    npm run build
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
else
    echo "Did not build the function $FUNCTION_NAME correctly"
    exit
fi

echo "Building getCoordsFromAddress (from geofence-apis.template)"
FUNCTION_NAME="getCoordsFromAddress"
cd $source_dir/$FUNCTION_NAME
if is_python; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -t .
    fi
    zip -9r $FUNCTION_NAME.zip . -x test_getCoordsFromAddress.py
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
elif [ -f "package.json" ]; then
    if [ -f "package-lock.json" ]; then 
        rm -rf package-lock.json
    fi
    npm run build
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
else
    echo "Did not build the function $FUNCTION_NAME correctly"
    exit
fi

echo "Building sendMessage (from geofence-apis.template)"
FUNCTION_NAME="sendMessage"
cd $source_dir/$FUNCTION_NAME
if is_python; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -t .
    fi
    zip -9r $FUNCTION_NAME.zip . -x test_sendMessage.py
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
elif [ -f "package.json" ]; then
    if [ -f "package-lock.json" ]; then 
        rm -rf package-lock.json
    fi
    npm run build
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
else
    echo "Did not build the function $FUNCTION_NAME correctly"
    exit
fi

echo "Building manageMessages (from geofence-apis.template)"
FUNCTION_NAME="manageMessages"
cd $source_dir/$FUNCTION_NAME
if is_python; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -t .
    fi
    zip -9r $FUNCTION_NAME.zip . -x test_manageMessages.py
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
elif [ -f "package.json" ]; then
    if [ -f "package-lock.json" ]; then 
        rm -rf package-lock.json
    fi
    npm run build
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
else
    echo "Did not build the function $FUNCTION_NAME correctly"
    exit
fi

echo "Building cognitoPosConfirmation (from geofence-apis.template)"
FUNCTION_NAME="cognitoPosConfirmation"
cd $source_dir/$FUNCTION_NAME
if is_python; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -t .
    fi
    zip -9r $FUNCTION_NAME.zip . -x test_cognitoPosConfirmation.py
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
elif [ -f "package.json" ]; then
    if [ -f "package-lock.json" ]; then 
        rm -rf package-lock.json
    fi
    npm run build
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
else
    echo "Did not build the function $FUNCTION_NAME correctly"
    exit
fi

echo "Building indexDdbDataToEs (from geofence-analytics.template)"
FUNCTION_NAME="indexDdbDataToEs"
cd $source_dir/$FUNCTION_NAME
if is_python; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -t .
    fi
    zip -9r $FUNCTION_NAME.zip .
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
elif [ -f "package.json" ]; then
    if [ -f "package-lock.json" ]; then 
        rm -rf package-lock.json
    fi
    npm run build
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
else
    echo "Did not build the function $FUNCTION_NAME correctly"
    exit
fi

echo "Building es-custom-resource-js (from geofence-analytics.template)"
FUNCTION_NAME="es-custom-resource-js"
cd $source_dir/$FUNCTION_NAME
npm ci
if [ $? -eq 0 ]; then 
    zip -9r $FUNCTION_NAME.zip .
    echo "Modules installed and function compressed properly"
else
    echo "Did not install node_modules correctly - see output above"
    exit
fi
cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
rm -rf node_modules && rm -rf $FUNCTION_NAME.zip 

echo "Building lambda-custom-resource"
FUNCTION_NAME="lambda-custom-resource"
cd $source_dir/$FUNCTION_NAME
if is_python; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -t .
    fi
    zip -9r $FUNCTION_NAME.zip .
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
elif [ -f "package.json" ]; then
    npm run build
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
else
    echo "Did not build the function $FUNCTION_NAME correctly"
    exit
fi

echo "Building website-custom-resource"
FUNCTION_NAME="website-custom-resource"
cd $source_dir/$FUNCTION_NAME
if is_python; then
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -t .
    fi
    zip -9r $FUNCTION_NAME.zip .
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
elif [ -f "package.json" ]; then
    npm run build
    cp ./$FUNCTION_NAME.zip $build_dist_dir/$FUNCTION_NAME.zip
    clean_up
else
    echo "Did not build the function $FUNCTION_NAME correctly"
    exit
fi

echo "------------------------------------------------------------------------------"
echo "[Build] Copying additional stacks and building the website"
echo "------------------------------------------------------------------------------"
# if you need additional stacks to be called by your main stack, make sure they are copied to $build_dist_dir

echo "Building the website"
WEBSITE="website-contents"
cd $source_dir/$WEBSITE
npm ci 
if [ $? -eq 0 ]; then
    npm run build
    if [ $? -ne 0 ]; then
        echo "Did not build and copy the website to the regional-s3-assets."
        exit
    fi
else
    echo "Did not install node_modules correctly - see output above"
    exit
fi
cp ./$WEBSITE.zip $build_dist_dir/$WEBSITE.zip
rm -rf node_modules && rm -rf build && rm -rf $WEBSITE.zip

fi 

#echo "Copying the website stack"
#STACK_NAME="website-stack"
#cd $source_dir/$STACK_NAME
#cp ./$STACK_NAME.yaml $build_dist_dir/$STACK_NAME.yaml

#echo "Copying the custom-resources stack"
#STACK_NAME="custom-resources-stack"
#cd $source_dir/$STACK_NAME
#cp ./$STACK_NAME.yaml $build_dist_dir/$STACK_NAME.yaml

#echo "Copying the elasticsearchkibana stack"
#STACK_NAME="elasticsearchkibana"
#cd $source_dir/$STACK_NAME
#cp ./$STACK_NAME.yaml $build_dist_dir/$STACK_NAME.yaml