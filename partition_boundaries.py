#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import re
import sys

try:
    text_type = unicode  # Python 2
except NameError:
    text_type = str      # Python 3


def main(disk_size=8, root_size=2):
    if not isinstance(disk_size, int):
        disk_size = int(disk_size)

    if not isinstance(root_size, int):
        root_size = int(root_size)

    try:
        data = get_partitions_boundaries(
            lines=sys.stdin.read().splitlines(),
            disk_size=disk_size, root_size=root_size)

        print(" ".join([text_type(x) for x in data]))

    except Exception as exp:
        print("Error: {}".format(repr(exp)))
        sys.exit(1)


def get_partitions_boundaries(lines, disk_size, root_size):

    sector_size = 512

    # parse all lines
    number_of_sector_match = []
    second_partition_match = []
    for line in lines:
        number_of_sector_match += re.findall(
            r"^Disk [0-9a-zA-Z\.\-\_]+\.img:.*, (\d+) sectors$", line)
        second_partition_match += re.findall(
            r"^[0-9a-zA-Z\.\-\_]+\.img\d +(\d+) +(\d+) +\d+ +\S+ +\d+ +Linux$",
            line)

    # ensure we retrieved nb of sectors correctly
    if len(number_of_sector_match) != 1:
        raise ValueError("cannot find the number of sector of disk")
    number_of_sector = int(number_of_sector_match[0])

    # ensure we retrieved the start of the root partition correctly
    if len(second_partition_match) != 1:
        raise ValueError(
            "cannot find start and/or end of root partition of disk")
    second_partition_start = int(second_partition_match[0][0])
    second_partition_end = int(second_partition_match[0][1])

    # whether disk is already full
    is_full = second_partition_end + 1 == number_of_sector
    if is_full:
        pass  # whether root part was already expanded

    # calculate new end of root
    disk_size_b = disk_size * 2 ** 30  # 8589934592
    nb_expected_clusters = disk_size_b // sector_size  # 16777216
    assert number_of_sector == nb_expected_clusters

    size_up_to_root_b = root_size * 2 ** 30  # 2147483648
    nb_clusters_endofroot = size_up_to_root_b // sector_size  # 4194304

    root_start = second_partition_start
    root_end = nb_clusters_endofroot

    data_start = root_end + 1
    data_end = nb_expected_clusters - 1

    return root_start, root_end, data_start, data_end


if __name__ == '__main__':
    main(*sys.argv[1:])
