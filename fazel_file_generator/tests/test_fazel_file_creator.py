# Licensed under the GPLv3 - see LICENSE
from pathlib import Path

from fazel_file_generator.fazel_file_creator import main

def test_fazel_file_creator(tmp_path):
    main("-f chime -s Crab -d 2015-06-01 -hs 16 -nh 1 -dt 1000 -q".split())
    filename = "fazel_crab_2015-06-01_chime.txt"
    p = Path(filename)
    assert p.exists()
    # Compare contents with reference
    with open(p) as f:
        fazel = f.readlines()
    with open(Path(__file__).parent / "data" / filename) as f:
        expected = f.readlines()
    assert fazel == expected
