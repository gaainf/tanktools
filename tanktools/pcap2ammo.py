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
import _version
from pcaper import PcapParser


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

    parser.add_argument('input', help='pcap file to parse')
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
    """Convert pcap to ammo file

    Args:
        args (dict): console arguments

    Returns:
        int: 0 if Success, 1 otherwise
    """

    if args['output']:
        file_handler = open(args['output'], "w")
    else:
        file_handler = sys.stdout

    reader = PcapParser()

    try:
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
                if 'content-type' in request.headers:
                    if request.headers['content-type'].lower().find('multipart/form-data') >= 0:
                        delete_headers(request, ["'content-length'"])
                        add_headers(request, ["'content-length: " + str(len(bytes(request.body, encoding="utf_8"))) + "'"])
                file_handler.write(make_ammo(request))
    except ValueError as e:
        sys.stderr.write('Error: ' + str(e) + "\n")
        return 1

    if args['output']:
        file_handler.close()

    return 0


def normalize_header_arg(header):
    """Remover enclosing quotes for header
       and transform it to the lower case

    Args:
        header (str): header with (or without) enclosing quotes

    Returns:
        str: header without enclosing quotes in lower case
    """
    norm_header = header.lower()
    if norm_header.startswith('"') or norm_header.startswith("'"):
        norm_header = norm_header[1:]
    if norm_header.endswith('"') or norm_header.endswith("'"):
        norm_header = norm_header[:-1]
    return norm_header


def delete_headers(request, headers):
    """Delete headers from http packet

    Args:
        request (HTTPRequest): HTTP request
        headers (list): headers to be added

    Returns:
        HTTPRequest: modified HTTP request
    """

    for header in headers:
        norm_header = normalize_header_arg(header)
        if norm_header in request.headers:
            del request.headers[norm_header]
    return request


def add_headers(request, headers):
    """Add headers to http packet.
       Parameter will be added if header is absent in original request.

    Args:
        request (HTTPRequest): HTTP request
        headers (list): headers to be added

    Returns:
        HTTPRequest: modified HTTP request
    """

    for header in headers:
        norm_header = normalize_header_arg(header)
        header_parts = re.split(r": *", norm_header, 1)
        if len(header_parts) == 2:
            header_name = header_parts[0].lower()
            header_value = header_parts[1]
            if header_name not in request.headers:
                request.headers[header_name] = header_value
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

    request_parts = [request.method + " " + request.uri + " HTTP/" + request.version,
                     "\n".join([(k + ": " + v) for k,v in request.headers.items()]),
                     (("\n" + request.body) if request.body else "")]
    request_string = "\n".join(request_parts) + "\n"
    ammo_template = (
        "%d %s\n"
        "%s"
    )
    request_length = len(bytes(request_string, encoding="utf_8"))
    return ammo_template % (request_length, case, request_string)


def main():
    """The main function"""

    args = parse_args()
    return pcap2ammo(args)


def init():
    """Testable init function"""

    if __name__ == '__main__':
        sys.exit(main())


init()
