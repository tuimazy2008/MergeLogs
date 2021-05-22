#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
Merged Log Generator script for merging logs by two given logs

Program:
    logs_merge.py

Example:
    python3 logs_merge.py path/to/log_a path/to/log_b -o path/for/output_log

Note:
    Input logs should be .jsonl format file
    Input logs should contain timestamp filed for each log line in format Y-M-D H:M:S
    for example: "timestamp": "2021-02-26 08:59:20"
"""

import os
import logging
import json

from argparse import ArgumentParser, RawTextHelpFormatter as Formatter
from datetime import datetime

__author__ = "Timur Galimov"
__mail__ = "galimov_timur@iclud.com"
__tool__ = "Logs merge"
__version__ = "0.1"

# Logging types
LOG_FORMAT = '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(lineno)d %(message)s'

LOG_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
JSON_TIMESTAMP_FIELD = 'timestamp'


class LogsMerger:
    """Class for logs merging"""

    def __init__(self):

        # Input logs
        self.log_a_path = None
        self.log_b_path = None
        # Output log
        self.output_log_path = None

        # Check input params
        self.parse_args()

    @staticmethod
    def get_log_time(line):
        """
        Gets time from logs line
        :param line: line from log jsonl file
        :raise JSONDecodeError - if json file decoding failed
        :raise JSONDecodeError - if couldn't get time from line
        :return: time extracted from timestamp or None
        """
        if not line:
            return None

        try:
            # Just alternative: time = re.search(r"([0-9]{4}\-[0-9]{2}\-[0-9]{2})", line).group(0)
            time = json.loads(line).get('timestamp')
            return datetime.strptime(time, LOG_DATETIME_FORMAT)

        except json.JSONDecodeError as err:
            logging.error("Parsing JSON line '{line}' failed with message: '{msg}'".format(line=line, msg=err.msg))
            raise err

        except ValueError as err:
            logging.error("Parsing JSON line '{line}' failed".format(line=line))
            raise err

    @staticmethod
    def validate_output(path):
        """
        :param path: output path argument value
        :raise: ValueError if wrong path is given
        :return: path if no errors
        """

        if path is None or path == "" or not path.endswith(".jsonl"):
            raise ValueError()

        return path

    @staticmethod
    def validate_input(path):
        """
        :param path: output path argument value
        :raise: ValueError if wrong path is given
        :return: path if no errors
        """

        if path is None or path == "" or not path.endswith(".jsonl") or not os.path.isfile(path):
            raise ValueError()

        return path

    @staticmethod
    def write_logs_until(fd_in, fd_out, stop_time):
        """
        :param fd_in: file descriptor to read from
        :param fd_out: file descriptor to write to
        :param stop_time: time until we should write
         """
        while True:
            # Get new line
            next_out_log_line = fd_in.readline()

            # If line contain time that exceeds minimal time from another file
            if not next_out_log_line:
                return None
            elif stop_time and LogsMerger.get_log_time(next_out_log_line) > stop_time:
                return next_out_log_line

            # Write line in out log
            fd_out.write(next_out_log_line)

    def parse_args(self):
        """
        Initialize and check arguments
        """
        parser = ArgumentParser(formatter_class=Formatter, description=__doc__)

        parser.add_argument('log_a',
                            help="Path to log file A",
                            type=LogsMerger.validate_input)

        parser.add_argument('log_b',
                            help="Path to log file B",
                            type=LogsMerger.validate_input)

        parser.add_argument('-o', '--output',
                            help="Path to the output log file",
                            default="Output.jsonl",
                            type=LogsMerger.validate_output,
                            required=False)

        args = parser.parse_args()

        logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)

        if len(set([args.log_a, args.log_b, args.output])) < 3:
            raise ValueError("Files shouldn't be the same")

        self.log_a_path = args.log_a
        self.log_b_path = args.log_b
        self.output_log_path = args.output

        # Delete file if exists
        if os.path.isfile(self.output_log_path):
            os.remove(self.output_log_path)

        logging.info("Input log A: {log_a},\n"
                     "Input log B: {log_b},\n"
                     "Output log: {output_log}".format(
                            log_a=self.log_a_path,
                            log_b=self.log_b_path,
                            output_log=self.output_log_path))

    def merge(self):
        """
        Read two log files and merge them into output one
        """
        with open(self.log_a_path) as fd_a, open(self.log_b_path) as fd_b, open(self.output_log_path, 'w') as fd_out:

            line_a = line_b = None
            while True:
                # Read line from each file
                line_a = fd_a.readline() if not line_a else line_a
                line_b = fd_b.readline() if not line_b else line_b

                if not line_a and not line_b:
                    break

                # Get time from log line
                time_a, time_b = LogsMerger.get_log_time(line_a), LogsMerger.get_log_time(line_b)

                # If log_B is ended, then write log_A until the end, OR if time_A < B write from log_A until time time_B
                if not time_b or (time_a and time_a < time_b):
                    # First line was already read, so we can write it
                    fd_out.write(line_a)
                    # Write next lines from log_A until time from B
                    line_a = LogsMerger.write_logs_until(fd_a, fd_out, time_b)
                    # Next time is time_B so we can write this log
                    fd_out.write(line_b)
                    line_b = None

                # Opposite situation
                elif not time_a or time_a > time_b:
                    fd_out.write(line_b)
                    line_b = LogsMerger.write_logs_until(fd_b, fd_out, time_a)
                    fd_out.write(line_a)
                    line_a = None

                # Same time in both files
                else:
                    fd_out.write(line_a)
                    fd_out.write(line_b)
                    line_a = line_b = None

def main():
    LogsMerger().merge()


if __name__ == '__main__':
    main()
