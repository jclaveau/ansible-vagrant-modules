#!/bin/sh

#wrapper to get to vagrant dynamic inventory

SCRIPT=`realpath $0`
SCRIPTPATH=`dirname $SCRIPT`


vagrantfile_dir=${SCRIPTPATH}/../../.vagrant
vagrantinventory_dir=${SCRIPTPATH}/../vagrant
vagrantinventory=${vagrantinventory_dir}/vagrant.py


cd $vagrantfile_dir
#passing all params to vagrant inventory script
$vagrantinventory $*
