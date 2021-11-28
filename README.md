# Logs merger #

## Description ##
```
Given two files with logs in JSON format, example:
…
{"timestamp": "2021-02-26 08:59:20", "log_level": "INFO", "message": "Hello"}
{"timestamp": "2021-02-26 09:01:14", "log_level": "INFO", "message": "Crazy"}
{"timestamp": "2021-02-26 09:03:36", "log_level": "INFO", "message": "World!"}
…
Messager in each files are sorted by timestamp field
Create script for merging given log files, result should be sorted by timestamp as well.

In order to generate input files given script log_generator.py:
log_generator.py <path/to/dir>

Command for the resulted script
<your_script>.py <path/to/log1> <path/to/log2> -o <path/to/merged/log>
```
