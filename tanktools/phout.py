#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Alexander Grechin
#
# Licensed under the BSD 3-Clause license.
# See LICENSE file in the project root for full license information.
#

""" Parse Yandex-tank output file

phout file format:
    'time' - timestamp
    'tag' - request tag
    'interval_real' - connect_time + send_time + latency + receive_time (mks)
    'connect_time' - time to establish connection to the server (mks)
    'send_time' - time to send request to the server (mks)
    'latency' - lag for the server response (mks)
    'receive_time' - time to receive response from the server (mks)
    'interval_event' - time to wait for response from the server (mks)
    'size_out' - request size (bytes)
    'size_in' - answer size (bytes)
    'net_code' - network response code
    'proto_code' - protocol response code

"""

import datetime
import dateutil
import pandas as pd

PHOUT_FIELDS = ['time',
                'tag',
                'interval_real',
                'connect_time',
                'send_time',
                'latency',
                'receive_time',
                'interval_event',
                'size_out',
                'size_in',
                'net_code',
                'proto_code']


def stop_criteria(index, date, flags):
    """Check stop criteria

    Args:
        index (int): index of current element
        date (datetime): date of current element
        flags (dict): List of flags:
            from_date: use only requests after specified date
            to_date: use only requests before specified date
            limit: use N requests from the beginning of file or specified date

    Returns:
        bool: returns true if stop criteria is achieved
    """

    result = False
    if 'to_date' in flags:
        result = date >= flags['to_date']
    if 'limit' in flags:
        result = index >= flags['limit']
    return result


def start_criteria(date, flags):
    """Check start criteria

    Args:
        date (datetime): date of current element
        flags (dict): List of flags

    Returns:
        bool: returns true if start criteria is achieved
    """

    result = True
    if 'from_date' in flags:
        result = date >= flags['from_date']
    return result


def parse_phout(input_file, flags=None):
    """Parse yandex-tank phout file and convert to DataFrame

    Args:
        input_file (str): input file path
        flags (dict): List of flags

    Returns:
        DataFrame: parsed records
    """

    flags = flags or []
    data = []
    if 'to_date' in flags:
        flags['to_date'] = float(dateutil.parser.parse(
            flags['to_date']).strftime("%s.%f"))
    if 'from_date' in flags:
        flags['from_date'] = float(dateutil.parser.parse(
            flags['from_date']).strftime("%s.%f"))
    if 'limit' in flags:
        flags['limit'] = int(flags['limit'])
    index = 0

    file_handler = open(input_file, 'r')
    for line in file_handler:
        line = line.strip(" \r\n\t")
        if not line:
            break
        elems = line.split("\t")
        if len(elems) != len(PHOUT_FIELDS):
            raise ValueError(
                "Incorrect fields count in line " +
                str(index + 1) + ": \"" + line + "\""
            )
        elems[0] = float(elems[0])
        if not start_criteria(elems[0], flags):
            continue
        data.append(elems)
        index = index + 1
        if stop_criteria(index, elems[0], flags):
            break
    data_frame = pd.DataFrame(data, columns=PHOUT_FIELDS)
    data_frame[[
        'interval_real',
        'connect_time',
        'send_time',
        'latency',
        'receive_time',
        'interval_event',
        'size_out',
        'size_in',
        'net_code',
        'proto_code'
    ]] = data_frame[[
        'interval_real',
        'connect_time',
        'send_time',
        'latency',
        'receive_time',
        'interval_event',
        'size_out',
        'size_in',
        'net_code',
        'proto_code'
    ]].astype(int)
    return data_frame


def size(data_frame):
    """Get rows count

    Args:
        data_frame (DataFrame): data

    Returns:
        int: rows count
    """

    return data_frame.shape[0]


def subset(data_frame, start, offset):
    """Get rows from start to start + offset

    Args:
        data_frame (DataFrame): data
        start (int): start row index
        offset (int): offset

    Returns:
        DataFrame: data_frame subset
    """

    return data_frame.iloc[start:start + offset]


def get_quantiles(data_frame, field_name, quantile_list=None):
    """Get quantiles for specific field

    Args:
        data_frame (DataFrame): data
        field_name (str): data_frame column name
        quantile_list (list): list of quantile values

    Returns:
        list: list of counted quantiles
    """

    if not quantile_list:
        quantile_list = [0.1, 0.2, 0.3, 0.4, 0.5,
                         0.6, 0.7, 0.8, 0.9, 0.95,
                         0.98, 0.99, 1.0]
    data_frame[field_name] = data_frame[field_name].fillna(0).astype(int)
    quantiles = data_frame[field_name].quantile(quantile_list)
    quantiles = quantiles.to_frame().reset_index()
    quantiles.rename(columns={'index': 'quantile'}, inplace=True)
    return quantiles


def print_quantiles(data_frame, field_name, quantile_list=None):
    """Print quantiles for specific field

    Args:
        data_frame (DataFrame): data
        field_name (str): data_frame column name
        quantiles (list): list of quantile values
    """

    quantiles = get_quantiles(data_frame, field_name, quantile_list)

    from_date = data_frame.iloc[0].time
    to_date = data_frame.iloc[-1].time
    print("\nPercentiles for %d requests\n \
    from %s\n \
    to   %s:" % (
        data_frame.shape[0],
        datetime.datetime.fromtimestamp(float(from_date)).
        strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
        datetime.datetime.fromtimestamp(float(to_date)).
        strftime('%Y-%m-%d %H:%M:%S.%f')[:-3],
    ))

    quantiles['quantile'] = quantiles['quantile'].apply(lambda x: x * 100)
    quantiles[field_name] = quantiles[field_name].fillna(0).astype(int)
    quantiles.rename(columns={'quantile': 'quantile (%)'}, inplace=True)
    quantiles.rename(columns={field_name: field_name + ' (mks)'}, inplace=True)
    print(
        quantiles.to_string(
            header=True,
            index=False,
            formatters={
                'quantile': '{:6.2f}'.format
            }
        )
    )


def get_rps(data_frame):
    """Calculate RPS for all requests

    Args:
        data_frame (DataFrame): data

    Returns:
        int: Requests per second
    """

    from_date = data_frame.iloc[0].time
    to_date = data_frame.iloc[-1].time
    duration = to_date - from_date
    if duration < 0:
        raise ValueError(
            "Incorrect time values from_date > to_data (%f > %f)" %
            (from_date, to_date)
        )
    if duration == 0:
        duration = 1
    requests_count = data_frame.shape[0]
    return requests_count/duration


def count_uniq_by_field(data_frame, field):
    """Count unique values for field

    Args:
        data_frame (DataFrame): data
        field (str): field name

    Returns:
        list: Statistics for HTTP responses
    """

    http_stats = data_frame.proto_code.value_counts().\
        rename_axis(field).reset_index(name='count')
    percent = data_frame.proto_code.value_counts(normalize=True)\
        * 100
    http_stats['percent'] = percent.values
    return http_stats


def print_http_reponses(data_frame):
    """Print stats for HTTP responses

    Args:
        data_frame (DataFrame): data
    """

    http_stats = count_uniq_by_field(data_frame, 'proto_code')
    http_stats.rename(columns={'proto_code': 'HTTP code'}, inplace=True)
    http_stats.rename(columns={'percent': 'percent (%)'}, inplace=True)
    print(
        http_stats.to_string(
            header=True,
            index=False,
            formatters={
                'percent (%)': '{:6.2f}'.format
            }
        )
    )
