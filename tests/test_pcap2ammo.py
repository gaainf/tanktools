#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Alexander Grechin
#
# Licensed under the BSD 3-Clause license.
# See LICENSE file in the project root for full license information.
#

import os
import mock
import pytest
import tempfile
import dpkt
from tanktools import pcap2ammo
import tanktools
import sys
import socket
from pcaper import pcap_gen


class TestParseHttp(object):

    # Fixtures

    def set_pcap_file(self, filename, data):
        """Prepare pcap file"""

        file_handler = open(filename, "wb")
        pcap_file = dpkt.pcap.Writer(file_handler)
        for packet in data:
            pcap_file.writepkt(packet['data'], packet['timestamp'])
        file_handler.close()

    @pytest.fixture()
    def prepare_data_file(self):
        """Prepare data file decorator"""

        filename = {'file': ''}

        def _generate_temp_file(*args, **kwargs):
            filename['file'] = tempfile.NamedTemporaryFile(delete=False).name
            self.set_pcap_file(filename['file'], args[0])
            return filename['file']

        yield _generate_temp_file

        # remove file after test
        if os.path.isfile(filename['file']):
            os.remove(filename['file'])

    @pytest.fixture()
    def remove_data_file(self, request):
        """Remove data file decorator"""

        filename = {'file': ''}

        def _return_filename(*args, **kwargs):
            filename['file'] = tempfile.NamedTemporaryFile(delete=False) \
                .name
            return filename['file']

        yield _return_filename

        # remove file after test
        if os.path.isfile(filename['file']):
            os.remove(filename['file'])

    # Tests

    @pytest.mark.positive
    def test_pcap2ammo_version(self, capsys):
        """Check version output"""

        sys.argv.append('-v')
        with pytest.raises(SystemExit) as system_exit:
            with mock.patch.object(
                pcap2ammo.sys,
                'argv',
                ['pcap2ammo.py', '-v']
            ):
                pcap2ammo.main()
        assert system_exit.value.code == 0
        captured = capsys.readouterr()
        # for python2 captured.err
        # for python3 captured.out
        assert captured.err == tanktools.__version__ + "\n" or \
            captured.out == tanktools.__version__ + "\n", "unexpected output"

    @pytest.mark.positive
    def test_pcap2ammo_main(
        self,
        prepare_data_file,
        capsys
    ):
        """Check main function is worked out properly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        ethernet = pcap_gen.generate_custom_http_request_packet(http_request)
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)
        with mock.patch.object(
            pcap2ammo.sys, 'argv',
            ['pcap2ammo.py', filename]
        ):
            pcap2ammo.main()
        captured = capsys.readouterr()
        # for python2 captured.err
        # for python3 captured.out
        assert captured.out == \
            str(len(http_request)) + " \n" + \
            http_request, "unexpected output"

    @pytest.mark.positive
    def test_pcap2ammo_input_file(
        self,
        prepare_data_file,
        capsys
    ):
        """Check main function parse input file correctly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        ethernet = pcap_gen.generate_custom_http_request_packet(http_request)
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': None,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': None,
        })
        captured = capsys.readouterr()
        assert captured.out == \
            str(len(http_request)) + " \n" + \
            http_request, "unexpected output"

    @pytest.mark.positive
    def test_pcap2ammo_init(
        self,
        prepare_data_file
    ):
        """Check init function works correctly"""

        with mock.patch.object(pcap2ammo, "main", return_value=42):
            with mock.patch.object(pcap2ammo, "__name__", "__main__"):
                with mock.patch.object(pcap2ammo.sys, 'exit') as mock_exit:
                    pcap2ammo.init()
                    assert mock_exit.call_args[0][0] == 42

    @pytest.mark.positive
    def test_pcap2ammo_add_header(
        self,
        prepare_data_file,
        capsys
    ):
        """Check add-header argument works correctly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        http_request_with_referer = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                                    "Host: rambler.ru\r\n" + \
                                    "Content-Length: 0\r\n" + \
                                    "Referer: http://domain.com/\r\n\r\n"
        ethernet = pcap_gen.generate_custom_http_request_packet(http_request)
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': None,
            'stats_only': False,
            'add_header': ['Referer: http://domain.com/'],
            'delete_header': [],
            'filter': None,
        })
        captured = capsys.readouterr()
        assert captured.out == \
            str(len(http_request_with_referer)) + " \n" + \
            http_request_with_referer, "unexpected output"

    @pytest.mark.negative
    def test_pcap2ammo_add_header_wrong_format(
        self,
        prepare_data_file,
        capsys
    ):
        """Check wrong formated add-header argument is handled correctly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        ethernet = pcap_gen.generate_custom_http_request_packet(http_request)
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': False,
            'stats_only': False,
            'add_header': ['Referer'],
            'delete_header': [],
            'filter': None,
        })
        captured = capsys.readouterr()
        assert captured.err == \
            'Error: Wrong header format, expected ' + \
            "\"<header_name>: <header_value>\"\n", \
            "unexpected output"

    @pytest.mark.positive
    def test_pcap2ammo_delete_header(
        self,
        prepare_data_file,
        capsys
    ):
        """Check delete-header argument works correctly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        http_request_without_header = \
            "GET https://rambler.ru/ HTTP/1.1\r\n" + \
            "Host: rambler.ru\r\n\r\n"
        ethernet = pcap_gen.generate_custom_http_request_packet(http_request)
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': None,
            'stats_only': False,
            'add_header': [],
            'delete_header': ['content-length'],
            'filter': None,
            'http_filter': None,
        })
        captured = capsys.readouterr()
        assert captured.out == \
            str(len(http_request_without_header)) + " \n" + \
            http_request_without_header, "unexpected output"

    @pytest.mark.positive
    def test_pcap2ammo_filter(
        self,
        prepare_data_file,
        capsys
    ):
        """Check main function parse input file with filter correctly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        params = {
            'ip': {
                'src': socket.inet_aton('10.4.0.136')
            }
        }
        ethernet = pcap_gen.generate_custom_http_request_packet(
            http_request,
            params
        )
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)

        # match filter
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': False,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': 'ip.src == 10.4.0.136',
            'http_filter': None
        })
        captured = capsys.readouterr()
        assert captured.out == \
            str(len(http_request)) + " \n" + \
            http_request, "unexpected output"

        # unmatch filter
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': False,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': 'ip.src == 10.4.1.136',
            'http_filter': None,
        })
        captured = capsys.readouterr()
        assert captured.out == "", "unexpected output"

    @pytest.mark.positive
    def test_pcap2ammo_excluding_filter(
        self,
        prepare_data_file,
        capsys
    ):
        """Check main function parse input file
        with excluding filter correctly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        params = {
            'ip': {
                'src': socket.inet_aton('10.4.0.136')
            }
        }
        ethernet = pcap_gen.generate_custom_http_request_packet(
            http_request,
            params
        )
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)

        # unmatch filter
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': False,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': None,
            'http_filter': '"rambler" in http.uri',
        })
        captured = capsys.readouterr()
        assert captured.out == \
            str(len(http_request)) + " \n" + \
            http_request, "unexpected output"

        # excluding filter
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': False,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': None,
            'http_filter': '"rambler" not in http.uri'
        })
        captured = capsys.readouterr()
        assert captured.out == "", "unexpected output"

    @pytest.mark.positive
    def test_pcap2ammo_output_file(
        self,
        prepare_data_file,
        capsys
    ):
        """Check pcap2ammo write result in output file correctly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        ethernet = pcap_gen.generate_custom_http_request_packet(http_request)
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)
        output_filename = tempfile.NamedTemporaryFile(delete=False).name
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': output_filename,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': None,
            'http_filter': None
        })
        captured = capsys.readouterr()
        assert captured.out == "", "output is not empty"
        file_content = open(output_filename, 'rb').read().decode("utf-8")
        os.remove(output_filename)
        assert file_content == \
            str(len(http_request)) + " \n" + \
            http_request, "unexpected output file content"

    @pytest.mark.positive
    def test_pcap2ammo_http_filter(
        self,
        prepare_data_file,
        capsys
    ):
        """Check main function parse input file with filter correctly"""

        http_request = "GET / HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        params = {
            'ip': {
                'src': socket.inet_aton('10.4.0.136')
            }
        }
        ethernet = pcap_gen.generate_custom_http_request_packet(
            http_request,
            params
        )
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)

        # match filter
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': False,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': None,
            'http_filter': '"rambler.ru" == http.headers["host"]'
        })
        captured = capsys.readouterr()
        assert captured.out == \
            str(len(http_request)) + " \n" + \
            http_request, "unexpected output"

        # unmatch filter
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': False,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': None,
            'http_filter':  '"rambler.ru" != http.headers["host"]'
        })
        captured = capsys.readouterr()
        assert captured.out == "", "unexpected output"

    @pytest.mark.positive
    def test_pcap2ammo_stats_only(
        self,
        prepare_data_file,
        capsys
    ):
        """Check stats-only flag handled correctly"""

        http_request = "GET https://rambler.ru/ HTTP/1.1\r\n" + \
                       "Host: rambler.ru\r\n" + \
                       "Content-Length: 0\r\n\r\n"
        ethernet = pcap_gen.generate_custom_http_request_packet(http_request)
        data = [{
            'timestamp': 1489136209.000001,
            'data': ethernet.__bytes__()
        }]
        filename = prepare_data_file(data)
        pcap2ammo.pcap2ammo({
            'input': filename,
            'output': False,
            'stats_only': True,
            'add_header': [],
            'delete_header': [],
            'filter': None,
            'http_filter': None
        })
        captured = capsys.readouterr()
        assert captured.out == \
            "Stats:\n\ttotal: 1\n\tcomplete: 1\n\t" + \
            "incorrect: 0\n\tincomplete: 0\n", "unexpected output"

    @pytest.mark.negative
    def test_pcap2ammo_empty_input_file(
        self,
        capsys
    ):
        """Check empty input filename"""

        pcap2ammo.pcap2ammo({
            'input': None,
            'output': False,
            'stats_only': False,
            'add_header': [],
            'delete_header': [],
            'filter': None,
            'http_filter': None
        })
        captured = capsys.readouterr()
        assert captured.err == \
            "Error: input filename is not specified or empty\n", \
            "unexpected output"
