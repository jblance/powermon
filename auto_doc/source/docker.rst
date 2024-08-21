Using powermon with Docker
==========================

Installing Docker on pi raspberry pi
------------------------------------
**on a fresh raspbian lite install**

* install git ``sudo apt-get install git``
* install docker ``curl -fsSL https://get.docker.com -o get-docker.sh` and then `sudo sh get-docker.sh``
* allow current user to run containers ``sudo usermod -aG docker [user_name]``

Run powermon in docker (using docker hub image)
-----------------------------------------------

* assuming docker is installed (otherwise see previous section)
* pull image

.. code-block:: console
    :caption: pull powermon docker image

    $ docker pull jblance/powermon
    Using default tag: latest
    latest: Pulling from jblance/powermon
    8a1e25ce7c4f: Already exists 
    1103112ebfc4: Already exists 
    e71929d49167: Already exists 
    c529235f83c8: Already exists 
    a47354887c31: Already exists 
    22dedeb685d0: Pull complete 
    69254e400de9: Pull complete 
    a5ccada1c8dc: Pull complete 
    Digest: sha256:68ed3d15a40f3cd2f1b2c1cef9ae0f3c038c281bfe57afe3ea4ed57574c55c37
    Status: Downloaded newer image for jblance/powermon:latest
    docker.io/jblance/powermon:latest

.. code-block:: console

    $ docker images
    REPOSITORY          TAG       IMAGE ID       CREATED       SIZE
    jblance/powermon    latest    3822e3bee24a   2 days ago    198MB

* if wanted, add a simpler tag (for easier running)

.. code-block:: console

    $ docker tag jblance/powermon pm
    REPOSITORY          TAG       IMAGE ID       CREATED       SIZE
    pm                  latest    3822e3bee24a   2 days ago    198MB
    jblance/powermon    latest    3822e3bee24a   2 days ago    198MB

* run a test command

.. code-block:: console

    $ docker run --rm pm powermon -v
    Power Device Monitoring Utility, version: 1.0.5, python version: 3.12.2


Run development code in docker
------------------------------

* clone git repo
  * ensure you have setup ssh key for git https://docs.github.com/en/authentication/connecting-to-github-with-ssh
  * clone repo ``git clone git@github.com:jblance/powermon.git``
* build an image and tag it ``$ docker build -t pm .``
* then commands can be run against it ``$ docker run --rm pm powermon -C /powermon/tests/config/test.yaml``

running a simple mqtt container
-------------------------------
``docker run --rm  --network=host -v ./docker/mosquitto/config:/mosquitto/config eclipse-mosquitto``

