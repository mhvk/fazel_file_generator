****************************************************
Algonquin Radio Observatory Fazel File creation code
****************************************************

.. image:: http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat
    :target: http://www.astropy.org
    :alt: Powered by Astropy Badge

.. image:: https://github.com/mhvk/screens/workflows/CI/badge.svg
   :target: https://github.com/mhvk/screens/actions
   :alt: Test Status

A fazel file is used for ARO 46m pointing-control. It contains a sequence of
Azimuth angle and Elevation angle that tells where the telescope should point
at.

File format
~~~~~~~~~~~

The first line is a header denoted by '#'. The date, followed by the Azimuth
angle (Deg Min Sec), followed by Azimuth Rate (deg/s), followed by the
Elevation angle (Deg Min Sec), followed by Elevation rate (deg/s).

The date format is YYYY.DDD.HH:MM:SS (yday with some formatting in astropy),
where DDD is the day number of the year. Also, azimuth and elevation rates are
not actually used by the pointing system, but their fields need to be occupied
for formatting's sake.

The current version of the Fazel file generator will also plot the source
position during the observation, and tells you if either the source dips below
the horizon, or if you may encounter the cable wrap issue. In these cases,
double check the observation schedule.

.. Installation

Installation instructions
=========================

The package and its dependencies can be installed with::

  pip install git+https://github.com/mhvk/fazel_file_generator.git#egg=fazel_file_generator

Typically, one might as well use a virtual environment, i.e., precede the
above with::

  python -m venv fazel
  source fazel/bin/activate

Usage
=====

Sample usage to get a fazel file to observe the Crab now using the CHIME feed::

  fazel_file_creator -f chime -s Crab -d 2015-06-01 -hs 16

For more information, do ``fazel_file_creator -h``.

License
=======

This project is Copyright (c) Rob Main, Fang Xi Lin, Daniel Baker, Jing Luo, Marten H. van Kerkwijk and licensed under
the terms of the GNU GPL v3+ license. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause licence. See the licenses folder for
more information.

Contributing
============

We love contributions! fazel_file_generator is open source, and it is needed
by everyone at the 46m. So, if you find a bug, raise an issue, or make a PR!
