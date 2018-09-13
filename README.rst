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

.. code:: python

    flags['from_date'] = '2018-01-18 20:09:50.123'
    flags['to_date'] = '2018-01-18 20:10:00.456'
    data = phout.parse_phout(args.input, flags)

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

    Pay attention, any timings are calculated in microseconds.

Print median of latency
***********************

.. code:: python

    data = phout.parse_phout('phout.log')
    print(data.latency.median())

Get RPS
*******

.. code:: python

    data = phout.parse_phout('phout.log')
    rps = phout.get_total_rps(data)


Select 200 OK status codes and calculate RPS
********************************************

.. code:: python

    data = phout.parse_phout('phout.log')
    selected_http_responses = data[data.proto_code == 200]
    rps = phout.get_total_rps(selected_http_responses)
    print("\n\nTotal RPS for %s: %.2f" % (200 OK, rps))

Print average request/response size
***********************************

.. code:: python

    print("Avg. Request / Response: %d / %d bytes." % (
        data.size_in.astype(float).mean(),
        data.size_out.astype(float).mean()
    ))

.. note::

    Pay attention it is required to convert data to float for correct work of ``mean`` function

Print RPS at Nth request
************************

.. code:: python

    chunk_size = int(phout.size(data) / 2)
    for start in range(0, phout.size(data), chunk_size):
        data_subset = phout.subset(data, start, chunk_size)
        print("RPS at request %s: %d" %
              (start + chunk_size, phout.get_total_rps(data_subset)))
