#!/bin/sh

#args
VAGRANTFILE_IN="$1"
#BOX_NAME=
BOXPATH_OUT="$2"
#BOXPATH_OUT=nopth
BOX_FN=$(basename "${BOXPATH_OUT}")
BOX_DIR=$(dirname "${BOXPATH_OUT}")

VAGRANTFILE_DIR=$(dirname "${VAGRANTFILE_IN}")


cd $VAGRANTFILE_DIR
#env variable for vagrant. NOT a path!!
VAGRANT_VAGRANTFILE=$(basename ${VAGRANTFILE_IN})

VAGRANT_VAGRANTFILE=${VAGRANT_VAGRANTFILE} vagrant up #$BOX_NAME ...etc.
shift 2
VAGRANT_VAGRANTFILE=${VAGRANT_VAGRANTFILE} vagrant package \
	--vagrantfile ${VAGRANT_VAGRANTFILE} \
	--output ${BOX_FN} \
	"$@"
#last args are for --include option

#to get it to work in cygwin!
mv $BOX_FN $BOX_DIR

VAGRANT_VAGRANTFILE=${VAGRANT_VAGRANTFILE} vagrant destroy -f
