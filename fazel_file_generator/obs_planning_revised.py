"""
change the accuracy of time to second
"""

import numpy as np
import astropy.units as u
from astropy.coordinates import AltAz
from astropy.utils import iers

iers.conf.iers_auto_url_mirror = "https://datacenter.iers.org/data/9/finals2000A.all"
iers.conf.iers_auto_url = "https://datacenter.iers.org/data/9/finals2000A.all"
iers.IERS_A_URL = "https://datacenter.iers.org/data/9/finals2000A.all"


def get_altaz(source, dish, time0, dtime):
    frame = AltAz(obstime=time0 + dtime, location=dish)
    altazs = source.transform_to(frame)
    return altazs


def get_offsets(altazs, daz0, dalt0, alt0, tol0):
    daz = daz0 * np.cos(alt0) / np.cos(altazs.alt)
    alt2 = altazs.alt + dalt0
    az2 = altazs.az + daz
    tol = tol0 * np.cos(alt0) / np.cos(altazs.alt)
    return daz, dalt0, az2, alt2, tol


def time_str(time):
    times = time.yday
    times = times[:4] + "." + times[5:8] + "." + times[9:-4]
    return times


def fazel_file(filename, header, midnight, delta_midnight, az, alt):
    f = open(filename, "w")
    f.write(header)
    for i in np.arange(len(delta_midnight)):
        azPrint, altPrint = az[i].to_string(sep=" "), alt[i].to_string(sep=" ")
        b = azPrint.split(" ")
        azPrint = "%d %d %.1f" % (int(b[0]), int(b[1]), float(b[2]))
        b = altPrint.split(" ")
        altPrint = "%d %d %.1f" % (int(b[0]), int(b[1]), float(b[2]))

        f.write(
            time_str(midnight + delta_midnight[i])
            + " "
            + azPrint
            + " -0.0 "
            + altPrint
            + " -0.0\n"
        )
    f.close()


def make_fazel_file(source, sname, feed, midnight, dur, location):
    if feed == "chime":
        dalt = -3.45 * u.deg
        daz0 = -3.25 * u.deg
        alt0 = 11.90 * u.deg
        tol0 = 0.1
    elif feed == "hirax":
        dalt = 0.0 * u.deg
        daz0 = 0.0 * u.deg
        alt0 = 0.0 * u.deg
        tol0 = 0.1
    elif feed == "nooffsets":
        dalt = 0.0 * u.deg
        daz0 = 0.0 * u.deg
        alt0 = 0.0 * u.deg
        tol0 = 0.1 * u.deg
    delta_midnight = np.linspace(0, dur, dur * 60 * 6 + 1) * u.hour
    daz, dalt, az2, alt2, tol = get_offsets(
        get_altaz(source, location, midnight, delta_midnight), daz0, dalt, alt0, tol0
    )
    header = (
        "# "
        + sname
        + " "
        + source.to_string("hmsdms")
        + " ; "
        + "alt_offset: "
        + str(dalt)
        + " ; az_offset: "
        + str(daz0)
        + " at alt="
        + str(alt0)
        + "\n"
    )
    filename = "fazel_" + sname + "_" + midnight.isot + "_hdr.txt"
    fazel_file(filename, header, midnight, delta_midnight, az2, alt2)
