#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Alexander Grechin
#
# Licensed under the BSD 3-Clause license.
# See LICENSE file in the project root for full license information.
#

"""Parser of Yandex-tank output file"""

import argparse
from tanktools import phout


def main():
    """Main function"""

    parser = argparse.ArgumentParser(prog=__file__, usage="%(prog)s [option]")

    parser.add_argument("-i", "--input", help="Input filepath")
    parser.add_argument(
        "--from-date", help="Parse requests only before specific date and time"
    )
    parser.add_argument(
        "--to-date", help="Parse requests only after specific date and time")
    parser.add_argument(
        "-l", "--limit", help="Set a limit of parserd requests")

    args = parser.parse_args()

    flags = {}
    if args.to_date:
        flags['to_date'] = args.to_date
    if args.from_date:
        flags['from_date'] = args.from_date
    if args.limit:
        flags['limit'] = args.limit

    quantile_list = [
        0.1, 0.2, 0.3, 0.4, 0.5,
        0.6, 0.7, 0.8, 0.9, 0.95,
        0.98, 0.99, 0.995, 1.0
    ]
    data = phout.parse_phout(args.input, flags)
    phout.print_quantiles(data, 'receive_time', quantile_list)
    phout.print_quantiles(data, 'latency', quantile_list)
    phout.print_quantiles(data, 'interval_real', quantile_list)

    rps = phout.get_total_rps(data)
    print("\n\nTotal RPS: %.2f" % rps)
    phout.print_http_reponses(data)

    http_responses = phout.count_uniq_by_field(data, 'proto_code')
    for http_code in http_responses['proto_code']:
        selected_http_responses = data[data.proto_code == http_code]
        rps = phout.get_total_rps(selected_http_responses)
        print("\n\nTotal RPS for %s: %.2f" % (http_code, rps))

    print("\n\nAvg. Request / Response: %d / %d bytes." % (
        data.size_in.astype(float).mean(),
        data.size_out.astype(float).mean()
    ))

    chunk_size = int(phout.size(data) / 2)
    for start in range(0, phout.size(data), chunk_size):
        data_subset = phout.subset(data, start, chunk_size)
        print("\n\nRPS at request %s: %d" %
              (start + chunk_size, phout.get_total_rps(data_subset)))


if __name__ == '__main__':
    main()
