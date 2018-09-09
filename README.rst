==============================
Yandex-tank output file parser
==============================

.. image:: https://travis-ci.org/travis-ci/travis-web.svg?branch=master
    :target: https://travis-ci.org/travis-ci/travis-web

.. image:: https://codecov.io/gh/gaainf/tanktools/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/gaainf/tanktools/

Yandex-tank prepare phout file with statistics after load test.
**tanktools** module helps to parse such files and convert to DataFrame.
You can use **pandas** module in manual mode to handle DataFrame
or use build-in `phout` functions.

So you can:

- calc quantiles

- get information about timings, LA, receive_time

- extract dataframes by microtime (and another column)

- group and analyze specific data like total/partial RPS,
  Avg. Request/Response time
