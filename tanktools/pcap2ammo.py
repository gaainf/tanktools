#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Alexander Grechin
#
# Licensed under the BSD 3-Clause license.
# See LICENSE file in the project root for full license information.
#

import argparse
import re
import sys
from . import _version
from pcaper import HTTPRequest


def parse_args():
    """Parse console arguments

    Returns:
        dict: console arguments
    """

    parser = argparse.ArgumentParser(
        description="Parse pcap file " +
                    "and convert HTTP requests to yandex-tank ammo",
        add_help=True
    )

    parser.add_argument(
        '-i', '--input', help='the pcap file to parse', required=True
    )
    parser.add_argument('-o', '--output', help='output ammo file')
    parser.add_argument('-f', '--filter', help='TCP/IP filter')
    parser.add_argument('-F', '--http-filter', help='HTTP filter')
    parser.add_argument(
        '-S', '--stats-only', help='print stats only', action='store_true'
    )
    parser.add_argument(
        '--add-header',
        action='append',
        type=str, default=[],
        help='add header to the each request'
    )
    parser.add_argument(
        '--delete-header',
        action='append',
        type=str, default=[],
        help='delete header from the each request'
    )

    parser.add_argument(
        '-v', '--version', help='print version', action='version',
        version='{version}'.format(version=_version.__version__)
    )

    return vars(parser.parse_args())


def pcap2ammo(args):
    """Convert pcap to ammo file"""

    if args['output']:
        file_handler = open(args['output'], "w")
    else:
        file_handler = sys.stdout

    reader = HTTPRequest()

    if args['stats_only']:
        for request in reader.read_pcap(args):
            pass
        print("Stats:")
        stats = reader.get_stats()
        for key in stats.keys():
            print("\t%s: %d" % (key, stats[key]))
    else:
        for request in reader.read_pcap(args):
            if 'delete_header' in args and args['delete_header']:
                delete_headers(request, args['delete_header'])
            if 'add_header' in args and args['add_header']:
                add_headers(request, args['add_header'])
            file_handler.write(make_ammo(request.origin))
    if args['output']:
        file_handler.close()

    return 0


def delete_headers(request, headers):
    """Delete headers from http packet

    Args:
        request (dpkt.http.Request): HTTP request
        headers (list): headers to be added

    Returns:
        dpkt.http.Request: modified HTTP reqquest
    """

    for header in headers:
        if header.lower() in request.headers:
            request.origin = re.sub(
                '^' + header + ".+?\r\n",
                '', request.origin,
                flags=re.IGNORECASE | re.MULTILINE)
            del request.headers[header.lower()]
    return request


def add_headers(request, headers):
    """Add headers to http packet.
       Parameter will be added if header is absent in original request.

    Args:
        request (dpkt.http.Request): HTTP request
        headers (list): headers to be added

    Returns:
        dpkt.http.Request: modified HTTP reqquest
    """

    for header in headers:
        arr = re.split(r": *", header, 1)
        if len(arr) == 2:
            if arr[0].lower() not in request.headers:
                request.origin = re.sub(
                    "\r\n\r\n",
                    "\r\n" + header + "\r\n\r\n", request.origin,
                    re.MULTILINE)
                request.headers[header.lower()] = header
        else:
            raise ValueError("Wrong header format, " +
                             "expected \"<header_name>: <header_value>\"")
    return request


def make_ammo(request, case=''):
    """Make phantom ammo file

    Args:
        request (str): HTTP request
        case (str):    ammo mark

    Returns:
        str: string in phantom ammo format
    """

    ammo_template = (
        "%d %s\n"
        "%s"
    )
    return ammo_template % (len(request), case, request)


def main():
    """The main function"""

    args = parse_args()
    pcap2ammo(args)


def init():
    """Testable init function"""

    if __name__ == '__main__':
        sys.exit(main())


init()
