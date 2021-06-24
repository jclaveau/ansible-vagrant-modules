#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [Jean Claveau (https://github.com/jclaveau)]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import sys
import subprocess


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# """
# This script call qemu with forced parameters which are not available through vagrant-libvirt directly
# Use it for debug if needed
# """

argv = sys.argv

args = ['qemu-system-x86_64']
i = 1
while i < len(argv):
    # if argv[i] == '-machine':
    #     args.append(argv[i])
        # args.append(argv[i + 1].replace('kvm', 'none'))
        # args.append(argv[i + 1].replace('kvm', 'hvf'))
        # args.append(argv[i + 1].replace('kvm', 'tcg'))
        # i += 2
        # continue
    args.append(argv[i])
    i += 1


print(subprocess.check_output(args).decode('utf-8'))

