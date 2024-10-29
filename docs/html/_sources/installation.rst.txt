Installation
============
powermon is packaged on pypi. There are a number of optional dependancies based on the usage required

.. code-block:: console
    :caption: installation examples

    user@host:~ $ pip install powermon           # minimal install
    user@host:~ $ pip install powermon[api]      # include web api dependancies
    user@host:~ $ pip install powermon[ble]      # include bluetooth dependancies
    user@host:~ $ pip install powermon[modbus]   # include modbus dependancies
    user@host:~ $ pip install powermon[systemd]  # include systemd dependancies
    user@host:~ $ pip install powermon[ble,dev]  # include bluetooth and development dependencies

    user@host:~ $ pip install powermon[dev]      # include all development dependancies
