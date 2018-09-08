Yandex-tank output file parser
==============================

Yandex-tank prepare phout file with statistics after load test.
**tanktools** module helps to parse such files and convert to DataFrame.
You can use **pandas** module in manual mode to handle DataFrame
or use build-in `phout` functions.

So you can:

- calc quantiles

- get information about timings, LA, receive_time

- extract dataframes by microtime (and another column)

- group and analyze only specific data
