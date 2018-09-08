#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Alexander Grechin
#
# Licensed under the BSD 3-Clause license.
# See LICENSE file in the project root for full license information.
#

import os
import dateutil
import pytest
from tanktools import phout


class TestPhout(object):
    def set_phout_data(self):
        """Prepare data in phout format"""

        return [
            "1516295382.983	#0	6201	281	94	5785	41	5991	26697	391	0	200",
            "1516295383.127	#1	5676	264	72	5315	25	5533	26697	390	0	200",
            "1516295383.189	#2	5547	248	67	5191	41	5400	26697	389	0	200",
            "1516295383.239	#3	5856	198	58	5581	19	5759	26697	391	0	200",
            "1516295383.282	#4	6045	232	59	5740	14	5954	26697	389	0	200",
            "1516295383.316	#5	4867	237	55	4555	20	4773	26697	388	0	200",
            "1516295383.349	#6	4877	224	58	4581	14	4792	26697	390	0	200",
            "1516295383.381	#7	5401	240	64	5079	18	5299	26697	390	0	200",
            "1516295383.409	#8	4766	198	54	4500	14	4683	26697	391	0	200",
            "1516295383.436	#9	5037	223	51	4750	13	4959	26697	390	0	200"
        ]

    def set_phout_file(self, filename, data):
        """Simplify input file creation"""

        file_handler = open(filename, "w")
        file_handler.write("\n".join(data))
        file_handler.close()

    @pytest.fixture()
    def prepare_data_file(self):
        """Prepare data file decoraotor"""

        # create file
        filename = "testfile.phout"
        data = self.set_phout_data()
        self.set_phout_file(filename, data)

        # return filename to test
        yield filename

        # remove file after test
        os.remove(filename)

    def test_phout_fields_struct_fields_count(self):
        """Check PHOUT_FIELDS constant format"""

        assert len(phout.PHOUT_FIELDS) == 12, "unexpected PHOUT_FIELDS format"

    def test_start_criteria_positive_limit_flag(self):
        """Check that stop_criteria hits if limit flag >= index
        and vice versa
        """

        flags = {'limit': 1}
        assert not phout.stop_criteria(0, None,
                                       flags), "limit flag should not hit"
        assert phout.stop_criteria(1, None, flags), "limit flag should hit"

    def test_stop_criteria_positive_to_date_flag(self):
        """Check that stop_criteria hits if date >= to_date flag
        and vice versa"""

        flags = {
            'to_date':
            float(
                dateutil.parser.parse('2018-01-18 20:09:50').strftime("%s.%f"))
        }
        date = float(
            dateutil.parser.parse('2018-01-18 20:09:50').strftime("%s.%f"))
        assert phout.stop_criteria(0, date, flags), "to_date flag should hit"

        date = float(
            dateutil.parser.parse('2018-01-18 20:09:51').strftime("%s.%f"))
        assert phout.stop_criteria(0, date, flags), "to_date flag should hit"

        date = float(
            dateutil.parser.parse('2018-01-18 20:09:49').strftime("%s.%f"))
        assert not phout.stop_criteria(
            0, date, flags), "to_date flag should not hit"

    def test_stop_criteria_negative_from_date_flag(self):
        """Check that stop_criteria doesn't take into account from_date flag"""

        flags = {
            'from_date':
            float(
                dateutil.parser.parse('2018-01-18 20:09:50').strftime("%s.%f"))
        }
        date = float(
            dateutil.parser.parse('2018-01-18 20:09:50').strftime("%s.%f"))
        assert not phout.stop_criteria(
            0, date, flags), "from_date flag should not hit"

        date = float(
            dateutil.parser.parse('2018-01-18 20:09:51').strftime("%s.%f"))
        assert not phout.stop_criteria(
            0, date, flags), "from_date flag should not hit"

        date = float(
            dateutil.parser.parse('2018-01-18 20:09:49').strftime("%s.%f"))
        assert not phout.stop_criteria(
            0, date, flags), "from_date flag should not hit"

    def test_start_criteria_positive_from_date_flag(self):
        """Check that start_criteria hits if date >= from_date flag
        and vice versa
        """

        flags = {
            'from_date':
            float(
                dateutil.parser.parse('2018-01-18 20:09:50').strftime("%s.%f"))
        }
        date = float(
            dateutil.parser.parse('2018-01-18 20:09:50').strftime("%s.%f"))
        assert phout.start_criteria(date, flags), "from_date flag should hit"

        date = float(
            dateutil.parser.parse('2018-01-18 20:09:51').strftime("%s.%f"))
        assert phout.start_criteria(date, flags), "from_date flag should hit"

        date = float(
            dateutil.parser.parse('2018-01-18 20:09:49').strftime("%s.%f"))
        assert not phout.start_criteria(
            date, flags), "from_date flag should not hit"

    def test_start_criteria_positive_to_date_flag(self):
        """Check that start_criteria doesn't take into account to_date flag"""

        flags = {
            'to_date':
            float(
                dateutil.parser.parse('2000-01-01 00:00:01').strftime("%s.%f"))
        }
        date = float(
            dateutil.parser.parse('2000-01-01 00:00:01').strftime("%s.%f"))
        assert phout.start_criteria(date, flags), "to_date flag should hit"

        date = float(
            dateutil.parser.parse('2000-01-01 00:00:02').strftime("%s.%f"))
        assert phout.start_criteria(date, flags), "to_date flag should hit"

        date = float(
            dateutil.parser.parse('2000-01-01 00:00:00').strftime("%s.%f"))
        assert phout.start_criteria(date, flags), "to_date flag should hit"

    @pytest.mark.usefixtures("prepare_data_file")
    def test_parse_phout_positive_parsing_fields_count(self,
                                                       prepare_data_file):
        """Check that positive phout file is parsed correctly"""

        result = phout.parse_phout(prepare_data_file)
        assert result.shape[0] == 10, "unexpected rows count"
        assert result.shape[1] == 12, "unexpected columns count"

    @pytest.mark.usefixtures("prepare_data_file")
    def test_parse_phout_positive_from_date_flag(self, prepare_data_file):
        """Check that positive phout file is parsed correctly"""

        flags = {'from_date': '2018-01-18 20:09:43.127'}
        result = phout.parse_phout(prepare_data_file, flags)
        assert result.shape[0] == 9, "unexpected rows count"
        assert result['latency'].iloc[
            0] == '5315', "unexpected the first element value"
        assert result['latency'].iloc[
            -1] == '4750', "unexpected the last element value"

    @pytest.mark.usefixtures("prepare_data_file")
    def test_parse_phout_positive_to_date_flag(self, prepare_data_file):
        """Check that positive phout file is parsed correctly"""

        flags = {'to_date': '2018-01-18 20:09:43.409'}
        result = phout.parse_phout(prepare_data_file, flags)
        assert result.shape[0] == 9, "unexpected rows count"
        assert result['latency'].iloc[
            0] == '5785', "unexpected the first element value"
        assert result['latency'].iloc[
            -1] == '4500', "unexpected the last element value"

    @pytest.mark.usefixtures("prepare_data_file")
    def test_parse_phout_positive_limit_flag(self, prepare_data_file):
        """Check that positive phout file is parsed correctly"""

        flags = {'limit': 1}
        result = phout.parse_phout(prepare_data_file, flags)
        assert result.shape[0] == 1, "unexpected rows count"
        assert result['latency'].iloc[
            0] == '5785', "unexpected the first element value"
        assert result['latency'].iloc[
            -1] == '5785', "unexpected the last element value"

    def test_parse_phout_negative_empty_lines_at_the_end(self):
        """Check that phout file with empty lines is parsed correctly"""

        filename = "testfile.phout"
        data = self.set_phout_data()
        data.extend(["", "", ""])
        self.set_phout_file(filename, data)
        result = phout.parse_phout(filename)
        assert result.shape[0] == 10, "unexpected rows count"
        assert result.shape[1] == 12, "unexpected columns count"
        os.remove(filename)

    def test_parse_phout_negative_incomplete_fields_count(self):
        """Check that phout file with incomplete or exceeded fields count
        in line leads to exception
        """

        filename = "testfile.phout"
        data = self.set_phout_data()
        data.append("a\tb")
        self.set_phout_file(filename, data)

        # check exception text
        with pytest.raises(
                ValueError, match=r'Incorrect fields count in line 11'):
            phout.parse_phout(filename)
        os.remove(filename)

        data = self.set_phout_data()
        data.append("1\t2\t3\t4\t5\t6\t7\t8\t9\t10\t11\t12\t13")
        self.set_phout_file(filename, data)

        # check exception text
        with pytest.raises(
                ValueError, match=r'Incorrect fields count in line 11'):
            phout.parse_phout(filename)
        os.remove(filename)

    @pytest.mark.skip(reason="format is not checked in parse_phout")
    def test_parse_phout_negative_incorrect_fields_format(self):
        """Check that phout file with incorrect fields in line leads
        to exception
        """

        filename = "testfile.phout"
        data = self.set_phout_data()
        data.append("a\tb\tc\td\te\tf\tg\th\ti\tj\tk\tl")
        self.set_phout_file(filename, data)

        # check exception text
        with pytest.raises(
                ValueError, match=r'Incorrect fields count in line 11'):
            phout.parse_phout(filename)
        os.remove(filename)

    @pytest.mark.usefixtures("prepare_data_file")
    def test_get_quantiles_positive_check_default_quantile_list(
            self, prepare_data_file):
        """Check that get_quantiles function returns expected result
        for default quantile_list
        """

        df = phout.parse_phout(prepare_data_file)
        quantiles = phout.get_quantiles(df, 'interval_real')
        assert quantiles['quantile'].values.tolist() == [
            0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 1
        ], "unexpected default quantile_list values"

    @pytest.mark.usefixtures("prepare_data_file")
    def test_get_quantiles_positive_check_custom_quantile_list(
            self, prepare_data_file):
        """Check that get_quantiles function returns expected result
        for custom quantile_list
        """

        df = phout.parse_phout(prepare_data_file)
        quantile_list = [
            0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99,
            0.995, 1
        ]
        quantiles = phout.get_quantiles(df, 'interval_real', quantile_list)
        assert quantiles['quantile'].values.tolist(
        ) == quantile_list, "unexpected quantile_list values"

    @pytest.mark.usefixtures("prepare_data_file")
    def test_get_quantiles_positive_check_latency(self, prepare_data_file):
        """Check that get_quantiles function returns expected result
        for latency field
        """

        df = phout.parse_phout(prepare_data_file)
        quantiles = phout.get_quantiles(df, 'latency')
        # check index
        assert quantiles['quantile'].values.tolist() == [
            0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 1
        ], "unexpected quantiles values"
        # check latency
        quantiles['latency'] = quantiles['latency'].astype(int)
        assert quantiles['latency'].values.tolist() == [
            4549, 4575, 4699, 4947, 5135, 5240, 5394, 5612, 5744, 5764, 5776,
            5780, 5785
        ], "unexpected quantiles values"

    @pytest.mark.usefixtures("prepare_data_file")
    def test_get_quantiles_positive_check_receive_time(self,
                                                       prepare_data_file):
        """Check that get_quantiles function returns expected result
        for receive_time field
        """

        data_frame = phout.parse_phout(prepare_data_file)
        quantiles = phout.get_quantiles(data_frame, 'receive_time')
        quantiles['receive_time'] = quantiles['receive_time'].astype(int)
        assert quantiles['receive_time'].values.tolist() == [
            13, 14, 14, 16, 18, 19, 21, 28, 41, 41, 41, 41, 41
        ], "unexpected quantiles values"

    @pytest.mark.usefixtures("prepare_data_file")
    def test_get_quantiles_positive_latency(self, prepare_data_file):
        """Check that get_quantiles function returns expected result
        for latency field
        """

        df = phout.parse_phout(prepare_data_file)
        quantiles = phout.get_quantiles(df, 'latency')
        # check index
        assert quantiles['quantile'].values.tolist() == [
            0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98, 0.99, 1
        ], "unexpected quantiles values"
        # check latency
        quantiles['latency'] = quantiles['latency'].fillna(0).astype(int)
        assert quantiles['latency'].values.tolist() == [
            4549, 4575, 4699, 4947, 5135, 5240, 5394, 5612, 5744, 5764, 5776,
            5780, 5785
        ], "unexpected quantiles values"

    def test_get_quantiles_negative_empty_data(self):
        """Check that get_quantiles function returns expected result
        for receive_time field
        """

        filename = "testfile.phout"
        self.set_phout_file(filename, [])
        df = phout.parse_phout(filename)

        quantiles = phout.get_quantiles(df, 'receive_time')
        quantiles['receive_time'] = quantiles['receive_time'].fillna(0).astype(
            int)
        assert quantiles['receive_time'].values.tolist() == [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        ], "quantiles should consist of 0 values"
        os.remove(filename)

    @pytest.mark.usefixtures("prepare_data_file")
    def test_print_quantiles_positive_check_output_format(
            self, capsys, prepare_data_file):
        """Check that print_quantiles function prints in expected format"""

        df = phout.parse_phout(prepare_data_file)
        phout.print_quantiles(df, 'latency')
        out, err = capsys.readouterr()
        expected_output = u"""
Percentiles for 10 requests
     from 2018-01-18 20:09:42.983
     to   2018-01-18 20:09:43.436:
quantile (%)  latency (mks)
        10.0           4549
        20.0           4575
        30.0           4699
        40.0           4947
        50.0           5135
        60.0           5240
        70.0           5394
        80.0           5612
        90.0           5744
        95.0           5764
        98.0           5776
        99.0           5780
       100.0           5785
"""
        assert out == expected_output, "unexpected output text"
        assert err == "", "error is absent"
