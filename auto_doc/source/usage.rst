Usage
=====
powermon usage ...

.. code-block:: console
    :caption: powermon command options

    $ powermon -h
    usage: powermon [-h] [-C [CONFIGFILE]] [--config CONFIG] [-V] [-v] [--listProtocols] [-1] [--force] [-D] [-I] [--adhoc ADHOC]

    Power Device Monitoring Utility, version: 1.0.10-dev, python version: 3.11.7

    options:
    -h, --help            show this help message and exit
    -C [CONFIGFILE], --configFile [CONFIGFILE]
                            Full location of config file
    --config CONFIG       Supply config items on the commandline in json format, 
                            eg '{"device": {"port":{"type":"test"}}, "commands": [{"command":"QPI"}]}'
    -V, --validate        Validate the configuration
    -v, --version         Display the version
    --listProtocols       Display the currently supported protocols
    -1, --once            Only loop through config once
    --force               Force commands to run even if wouldnt be triggered
                            (should only be used with --once)
    -D, --debug           Enable Debug and above (i.e. all) messages
    -I, --info            Enable Info and above level messages
    --adhoc ADHOC         Send adhoc command to mqtt adhoc command queue
                             - needs config file specified and populated

Standard usage is ``powermon -C /path/to/configfile.yaml`` 

Config file syntax is described in :doc:`config_file`