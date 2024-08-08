## Fazel File creation code
## Rob Main, Fang Xi Lin, Daniel Baker
## Last edited 2018-08-16

from pathlib import Path
from distutils.util import strtobool

import numpy as np
import matplotlib.pyplot as plt
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.table import QTable

from fazel_file_generator.obs_planning_revised import get_offsets, fazel_file

def load_source_list(filename="sources.ecsv"):
    # Load saved source locations
    p = Path(filename)
    if not p.exists():
        p = Path(__file__).parent / "data" / filename
    return {r["name"]: r["coord"] for r in QTable.read(p)}


def main(args=None):

    # Parse command line argument

    tc = Time.now()
    midnight = tc.iso[:10]
    ts_d = int((tc - Time(midnight)).to(u.h).value)

    source_list = load_source_list()

    import argparse

    parser = argparse.ArgumentParser(description="Fazel File Creation")
    parser.add_argument(
        "-s",
        "--source",
        type=str,
        help="Source name (eg. 'Cas A', 'PSR B1957+20')",
        required=True,
    )
    parser.add_argument(
        "-d",
        "--date",
        type=str,
        help="Date (yyyy-mm-dd) (defaults to current date)",
        default=midnight,
    )
    parser.add_argument(
        "-f",
        "--feed",
        type=str,
        default="chime",
        help="Which feed? (defaults to CHIME)",
        choices=["chime", "hirax", "4m", "xmas"],
    )
    parser.add_argument(
        "-hs",
        "--hour-start",
        type=int,
        help="Starting hour (24h format to closest hour) (defaults to start of current hour)",
        default=ts_d,
    )
    parser.add_argument(
        "-nh",
        "--number-hours",
        type=int,
        help="Observation length in hours (defaults to 4)",
        default=4,
    )
    parser.add_argument(
        "-dt",
        "--time-step",
        type=int,
        default=1,
        help="Time delta between pointings in seconds (defaults to 1)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        help="No output or plot, just make fazel file (default: False)",
        action="store_const",
        const=True,
    )

    args = parser.parse_args(args)

    # Convert to simplified source name
    source_name = args.source.lower().replace(" ", "")

    filename = "fazel_%s_%s_%s.txt" % (source_name, args.date, args.feed)


    # 3c286 = SkyCoord('13h31m08.29s','+30d30m33.0s')
    # casA = SkyCoord(350.866*u.deg, 58.8117*u.deg)
    # b0329 = SkyCoord('03h32m59.368s','+54d34m43.57s')

    # Load source coordinates
    if args.source in source_list.keys():
        source = source_list[args.source]
        source_found = True
    elif source_name in source_list.keys():
        source = source_list[source_name]
        source_found = True
    elif "psr" + source_name in source_list.keys():
        source = source_list["psr" + source_name]
        source_name = "psr" + source_name
        source_found = True
    else:
        try:
            if not args.quiet:
                print_("Source not found in common list, searching online")
            source = SkyCoord.from_name(args.source)
            source_found = False
        except Exception:
            try:
                source = SkyCoord.from_name("PSR " + args.source)
                source_name = "psr" + source_name
            except Exception:
                if args.quiet:
                    raise

                print("Source not found online, input coordinates manually? (y/n)")
                val2 = input()
                if strtobool(val2):
                    print("RA (astropy formats)")
                    ra_inpt = input()
                    print(r"Dec (astropy formats))")
                    dec_inpt = input()
                    source = SkyCoord(
                        ra=float(ra_inpt) * u.deg, dec=float(dec_inpt) * u.deg
                    )
                    source_found = False
                else:
                    print("Goodbye")
                    exit()


    # FOR OFFSET CHIME FEED (because it isnt on axis)
    if args.feed == "chime":
        dalt0 = -3.45 * u.deg
        daz0 = -3.25 * u.deg
    elif args.feed == "xmas":
        dalt0 = -3.45 * u.deg
        daz0 = 3.25 * u.deg
    else:
        dalt0 = 0 * u.deg
        daz0 = 0 * u.deg

    if not args.quiet:
        print("Creating Fazel file for     :", args.source)
        print("Date (UTC)                  :", args.date)
        print("Starting hour (0=midnight)  :", args.hour_start)
        print("Feed                        :", args.feed)
        print("Alt Offset                  :", dalt0)
        print("Az Offset                   :", daz0)
        print("Observation length          :", args.number_hours, "hours")
        print("Time step between pointings :", args.time_step, "seconds")
        print("Are these correct? (y/n)\n")

        val = input()
        if strtobool(val):
            print("Sky Coords")
            print("RA :", str(source.ra.hms))
            print("DEC:", str(source.dec.deg), "degrees")
            print("Are these correct? (y/n)\n")
            val2 = input()
            if strtobool(val2):
                pass
            else:
                print("RA (astropy formats)")
                ra_inpt = input()
                print(r"Dec (astropy formats))")
                dec_inpt = input()
                source = SkyCoord(ra=ra_inpt, dec=dec_inpt)
        else:
            print("Goodbye.")
            exit()

        print("Okay, computing stuff...")

    if not source_found:
        source_list[source_name] = source
        t = QTable([list(source_list.keys()), SkyCoord(list(source_list.values()))],
                   names=["name", "coord"])
        t.write("sources.ecsv", overwrite=True)


    # ARO location
    ARO = EarthLocation(918034.4879 * u.m, -4346132.3267 * u.m, 4561971.2292 * u.m)

    # Midnight of observation date
    midnight = Time("%s 00:00:00" % args.date)

    # Your start hour + n hours should just encompass your observation (it can be longer)
    # The hour that you want to start your observations
    hour_start = args.hour_start
    # The length of your observation in hours
    nhours = args.number_hours

    # This gets the time deltas for the observation pointings
    delta_midnight = (
        np.linspace(
            hour_start,
            hour_start + nhours,
            (nhours * 60 * 60 // (args.time_step)),
            endpoint=False,
        )
        * u.hour
    )

    altazs = source.transform_to(AltAz(obstime=midnight + delta_midnight, location=ARO))

    alt0 = 11.9 * u.deg
    tol0 = int(1) * u.deg

    daz, dalt0, az2, alt2, tol = get_offsets(altazs, daz0, dalt0, alt0, tol0)


    # Test if source is in Alt range of ARO
    if alt2.max() < alt0:
        raise ValueError("Source is not visible during specified run")

    alt_err = np.argwhere(np.diff(np.sign(alt2 - alt0)) > 0).flatten()
    if not args.quiet:
        if alt_err.shape[0] > 0:
            print("Source enters Alt range at:")
            print(midnight + delta_midnight[alt_err], "UTC")
        else:
            print("Source starts in Alt range")
    alt_err = np.argwhere(np.diff(np.sign(alt2 - alt0)) < 0).flatten()
    if not args.quiet:
        if alt_err.shape[0] > 0:
            print("Source leaves Alt range at:")
            print(midnight + delta_midnight[alt_err], "UTC")
        else:
            print("Source ends in Alt range")

        # Throw a warning if we are increasing across 40deg az or decreasing across 52deg az.
        cw1 = (51 - 11) * u.deg
        cw2 = (41 + 11) * u.deg
        cw_err = np.concatenate(
            (
                np.argwhere(np.diff(np.sign(az2 - cw1)) > 0).flatten(),
                np.argwhere(np.diff(np.sign(az2 - cw2)) < 0).flatten(),
            )
        )

        if cw_err.size > 0:
            print(
                "You might encounter the cable wrap issue at the following times. Check source by hand!"
            )
            print(midnight + delta_midnight[cw_err], "UTC")

        fig, ax = plt.subplots(nrows=2)
        ax[0].plot(delta_midnight, altazs.alt, label="Source Location")
        ax[0].plot(delta_midnight, alt2, label="Telescope Pointing")
        ax[0].axhline(10.3, color="k", ls="--", lw=2)
        ax[0].legend(loc=0)
        ax[0].set_xlim(delta_midnight[0].value, delta_midnight[-1].value)
        ax[0].set_title("%s Altitude" % args.source)
        ax[0].set_xlabel("UTC")
        ax[0].set_ylabel("Altitude (deg)")

        ax[1].plot(delta_midnight, altazs.az, label="Source Location")
        ax[1].plot(delta_midnight, az2, label="Telescope Pointing")
        ax[1].legend(loc=0)
        ax[1].set_xlim(delta_midnight[0].value, delta_midnight[-1].value)
        ax[1].set_title("%s Azimuth" % args.source)
        ax[1].set_xlabel("UTC")
        ax[1].set_ylabel("Azimuth (deg)")
        plt.tight_layout()
        plt.show(block=False)

        print("Are you happy with these ranges Dave? (y/n)")

        val = input()
        if strtobool(val):
            pass
        else:
            print("Goodbye")
            exit()

        print("Generating Fazel file", filename)

    # FIX THIS TO CHOOSE WHICH HEADER YOU WANT
    # IT IS GOOD TO PUT YOUR SOURCE, THE DATE OF OBSERVATION, AND THE FEED YOU ARE USING
    header = (
        "#%s Fazel for %s feed, %s, (yyyy.ddd.hh:mm:ss.SSS azimuthal_angle 0.1 elevation_angle 0.4)\n"
        % (args.source, args.feed, args.date)
    )

    # fazel_file('fazel_b0329_apr24_CHIME.txt', header, midnight, delta_midnight, az2, alt2)
    fazel_file(filename, header, midnight, delta_midnight, az2, alt2)
