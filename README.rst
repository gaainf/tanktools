====================================
Yandex-tank input/output file parser
====================================

.. image:: https://travis-ci.org/travis-ci/travis-web.svg?branch=master
    :target: https://travis-ci.org/travis-ci/travis-web

.. image:: https://codecov.io/gh/gaainf/tanktools/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/gaainf/tanktools/

.. image:: https://img.shields.io/badge/python-2.7-blue.svg
    :target: https://www.python.org/downloads/release/python-270/

.. image:: https://img.shields.io/badge/python-3.5-blue.svg
    :target: https://www.python.org/downloads/release/python-350/

.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :target: https://www.python.org/downloads/release/python-360/

.. image:: https://img.shields.io/pypi/l/tanktools.svg
    :target: https://github.com/gaainf/tanktools/blob/master/LICENSE


Yandex-tank prepare `phout` file with statistics after load testing.
**tanktools** module helps to parse such files and convert to DataFrame.
You can use **pandas** module in manual mode to handle DataFrame
or use build-in functions.

Generate Yandex-tank ammos from pcap or har files using `pcap2ammo`
or `har2ammo` scrips. HTTP requests are extracted completely
with headers and body.

So you can:

- calc quantiles

- get information about timings, latency, status codes

- extract requests by timestamp, tag and other columns

- group and analyze specific data like total/partial RPS,
  average request/response size

- calc statistical metrics

- convert pcap file to ammo

- convert har file to ammo

- filter out and modify requests on ammo generating


************
Installation
************
.. code:: python

    pip install tanktools

********
Examples
********

Select DataFrame by timestamp
*****************************

It is possible to parse a part of staistics by time and overal count

.. code:: python

    from tanktools import phout
    flags = {
        'from_date': '2018-01-18 20:09:50.123',
        'to_date'  : '2018-01-18 20:10:00.456',
        'limit': 100
    }
    data = phout.parse_phout('phout.log', flags)
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
    print("\n\nLatency median: %d ms" % int(data.latency.median() / 1000))

.. code::

    Latency median: 30 ms

Get RPS
*******

.. code:: python

    data = phout.parse_phout('phout.log')
    rps = phout.get_rps(data)

Print HTTP response statistics
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


*********
pcap2ammo
*********

Convert pcap file to Yandex-tank ammo
*************************************

.. code:: bash

    pcap2ammo file.pcap

.. code::

    73
    GET https://rambler.ru/ HTTP/1.1\r\n
    Host: rambler.ru\r\n
    Content-Length: 0\r\n\r\n

Count statistics about HTTP requests
***************************************

.. code:: bash

    pcap2ammo -S file.pcap

    Stats:
        total: 1
        complete: 1
        incorrect: 0
        incomplete: 0

Print to file
*************************************

.. code:: bash

    pcap2ammo -o out.ammo file.pcap

Add or delete headers
*********************
Applyed for all requests, containing specified headers

.. code:: bash

    pcap2ammo --add-header 'Referer: http://domain.com' --add-header 'X-Ip: 1.1.1.1' file.pcap

.. code:: bash

    pcap2ammo --delete-header 'Content-Length' file.pcap
    pcap2ammo --delete-header 'Connection' --add-header 'Connection: keep-alive' file.pcap

Filter TCP/IP packets
*********************

.. code:: bash

    pcap2ammo -f 'ip.src==10.10.10.10 and tcp.dport==8080' file.pcap

Filter HTTP packets
*********************

.. code:: bash

    pcap2ammo -F '"rambler.ru" in http.uri' file.pcap

You can use logical expressions in filters

.. code:: bash

    pcap2ammo -F '"keep-alive" in http.headers["connection"] or "Keep-alive" in http.headers["connection"]' file.pcap

String functions over HTTP headers

.. code:: bash

    pcap2ammo -F '"keep-alive" in http.headers["connection"].lower()' file.pcap

Use excluding filters also

.. code:: bash

    pcap2ammo -F '"rambler.ru" != http.headers["host"]' file.pcap

*********
har2ammo
*********

Convert pcap file to Yandex-tank ammo
*************************************

.. code:: bash

    har2ammo file.har

.. code::

    73
    GET https://rambler.ru/ HTTP/1.1\r\n
    Host: rambler.ru\r\n
    Content-Length: 0\r\n\r\n

Count statistics about HTTP requests
***************************************

.. code:: bash

    har2ammo -S file.har

    Stats:
        total: 1
        complete: 1
        incorrect: 0
        incomplete: 0

Print to file
*************************************

.. code:: bash

    har2ammo -o out.ammo file.har

Add or delete headers
*********************
Applyed for all requests, containing specified headers

.. code:: bash

    har2ammo --add-header 'Referer: http://domain.com' --add-header 'X-Ip: 1.1.1.1' file.har

.. code:: bash

    har2ammo --delete-header 'Content-Length' file.har
    har2ammo --delete-header 'Connection' --add-header 'Connection: keep-alive' file.har

Filter HTTP packets
*********************

.. code:: bash

    har2ammo -F '"rambler.ru" in http.uri' file.har

You can use logical expressions and python functions in filters

.. code:: bash

    har2ammo -F '"keep-alive" in http.headers["connection"] or "Keep-alive" in http.headers["connection"]' file.har
    har2ammo -F '"keep-alive" not in http.headers["connection"].lower()' file.har

Please, see more information about filters in `pcaper <https://github.com/gaainf/pcaper/>`_ package description.
