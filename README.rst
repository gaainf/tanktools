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

- extract data by timestamp and other columns

- group and analyze specific data like total/partial RPS,
  Avg. Request/Response size

******
Import
******
.. code:: python

    from tanktools import phout

********
Examples
********


Select DataFrame by timestamp
*****************************

It is possible to parse a part of staistics by time and overal count

.. code:: python

    flags = {
        'from_date': '2018-01-18 20:09:50.123',
        'to_date'  : '2018-01-18 20:10:00.456',
        'limit': 100
    }
    data = phout.parse_phout(args.input, flags)
    print("Total count: %d" % phout.size(data))

.. code::

    Total count: 100

Print percentiles
*****************
.. code:: python

        data = phout.parse_phout('phout.log')
        phout.print_quantiles(data, 'receive_time')

.. code::

    Percentiles for 150030 requests
        from 2018-01-18 20:09:42.983
        to   2018-01-18 20:10:55.108:
    quantile (%)  receive_time (mks)
            10.0                   9
            20.0                   9
            30.0                  10
            40.0                  10
            50.0                  10
            60.0                  10
            70.0                  11
            80.0                  12
            90.0                  13
            95.0                  14
            98.0                  16
            99.0                  17
            100.0                 716


.. note::

    Pay attention, timings are calculated in microseconds.

Print latency median
************************

.. code:: python

    data = phout.parse_phout('phout.log')
    # Convert and print timing in milliseconds
    print("\n\nLA median: %d ms" % int(data.latency.median() / 1000))

.. code::

    LA median: 30 ms

Get RPS
*******

.. code:: python

    data = phout.parse_phout('phout.log')
    rps = phout.get_rps(data)

Print HTTP responses statistics
*******************************

.. code:: python

    data = phout.parse_phout('phout.log')
    phout.print_http_reponses(data)

.. code::

    HTTP code   count  percent (%)
         500   83429        56.38
         200   61558        41.60
         502    2944         1.99
           0      41         0.03

Select 200 OK responses and print latency median
************************************************

.. code:: python

    data = phout.parse_phout('phout.log')
    selected_http_responses = data[data.proto_code == 200]
    print("Latency median for 200 OK: %d" %
          selected_http_responses.latency.median())

.. code::

    Latency median for 200 OK: 3539

Print average request/response size
***********************************

.. code:: python

    print("Avg. Request / Response: %d / %d bytes" % (
        data.size_in.astype(float).mean(),
        data.size_out.astype(float).mean()
    ))

.. code::

    Avg. Request / Response: 364 / 26697 bytes

.. note::

    Pay attention it is required to convert data to float for correct work of ``mean`` function

Print RPS at Nth request
************************

.. code:: python

    print("RPS at request:")
    chunk_size = int(phout.size(data) / 2)
    for start in range(0, phout.size(data), chunk_size):
        data_subset = phout.subset(data, start, chunk_size)
        print("\t%s: %.2f" %
              (start + chunk_size, phout.get_rps(data_subset)))

.. code::

    RPS at request:
        73986: 2062.50
        147972: 2530.56
