import argparse
import shutil
import os
import csv

from datetime import date
from fastkml import KML, Placemark
from fastkml.utils import find_all
from pathlib import Path
from time import time
from uuid import uuid4

OUTPUT_PATH = "out"
UUID = str(uuid4()).upper()


class COT:
    """
    COT (Cursor-on-Target) ATAK message data.

    In this particular implementation it represents only the marker data.
    """

    def __init__(self, callsign: str, lon: float, lat: float, remarks: str = ""):
        """
        Initialize object.

        :param lon:
            Longtitude.
        :param lat:
            Latitude.
        :param callsign:
            Callsing (name of the point).
        :param remarks:
            Remarks (additional not attached to the point).
        """
        self.lon = lon
        self.lat = lat
        self.callsign = callsign
        self.uuid = str(uuid4()).upper()
        self.time = date.fromtimestamp(time()).strftime("%Y-%m-%dT00:00:00Z")
        self.type = "a-u-G"
        self.how = "h-g-i-g-o"
        self.icon_path = "f7f71666-8b28-4b57-9fbb-e38e61d33b79/Google/ltblu-pushpin.png"
        self.remarks = remarks


def create_package(name: str, cots: list[COT]):
    """
    Create ATAK package.

    Package will contain all of the COTs passed to this function.
    PAckage will be saved as a ZIP file inside current working directory.

    :param name:
        Name of the package - will also be the name of the ZIP file.
    :param cots:
        List of COTs to embed inside package.
    """
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
    os.mkdir(OUTPUT_PATH)

    _create_manifest(name, cots)
    for cot in cots:
        _create_cot(cot)

    shutil.make_archive(name, "zip", root_dir="out")


def _indent_write(f, txt, indent=0):
    f.write(f'{' ' * 2 * indent}{txt}\n')


def _create_manifest(package_name: str, cots: list[COT]):
    output_path = Path(OUTPUT_PATH, 'MANIFEST')
    output_path.mkdir()
    manifest_path = Path(output_path, 'manifest.xml')

    with open(manifest_path, 'w') as f:
        _indent_write(f, '<?xml version="1.0" encoding="UTF-8"?>')
        _indent_write(f, '<MissionPackageManifest version="2">')
        _indent_write(f, '<Configuration>', 1)
        _indent_write(f, f'<Parameter name="name" value="{package_name}"/>', 2)
        _indent_write(
            f, f'<Parameter name="uid" value="{str(uuid4()).upper()}"/>', 2)
        _indent_write(f, '<Parameter name="remarks" value=""/>', 2)
        _indent_write(f, '</Configuration>', 1)
        _indent_write(f, '<Contents>', 1)
        for cot in cots:
            _indent_write(
                f, f'<Content zipEntry="{cot.uuid}/{cot.uuid}.cot" ignore="false">', 2)
            _indent_write(f, f'<Parameter name="uid" value="{cot.uuid}"/>', 3)
            _indent_write(f, '</Content>', 2)
        _indent_write(f, '</Contents>', 1)
        _indent_write(f, '</MissionPackageManifest>')


def _create_cot(cot: COT):
    output_path = Path(OUTPUT_PATH, cot.uuid)
    output_path.mkdir()
    cot_path = Path(output_path, f'{cot.uuid}.cot')

    with open(cot_path, 'w') as f:
        _indent_write(
            f, f'<event version="2.0" uid="{cot.uuid}" type="{cot.type}" how="{cot.how}" time="{cot.time}" start="{cot.time}" stale="{cot.time}">')
        _indent_write(
            f, f'<point lat="{cot.lat}" lon="{cot.lon}" hae="0.0" ce="0.0" le="0.0" />')
        _indent_write(f, '<detail>')
        _indent_write(f, f'<contact callsign="{cot.callsign}"/>')
        _indent_write(f, '<precisionlocation geopointsrc="???" altsrc="???"/>')
        _indent_write(f, '<status readiness="true"/>')
        _indent_write(f, '<archive/>')
        _indent_write(
            f, f'<link uid="{UUID}" production_time="{cot.time}" type="a-f-G-U-C" parent_callsign="ATAK Marker Import" relation="p-p"/>')
        _indent_write(f, f'<usericon iconsetpath="{cot.icon_path}"/>')
        _indent_write(f, '<color argb="-1"/>')
        _indent_write(
            f, '<_flow-tags_ TAK-Server-fe3bcbd8="2020-02-06T17:53:28Z"/>')
        _indent_write(f, f'<remarks>{cot.remarks}</remarks>')
        _indent_write(f, '')
        _indent_write(f, '</detail>')
        _indent_write(f, '</event>')

# Below is an example of creating a package from the KML file
def _export_kml():
    cots = _convert_kml('example.kml')
    create_package("Test_KML", cots)

def _convert_kml(kml_path: str) -> list[COT]:
    k = KML.parse(kml_path)

    waypoints = []
    for p in list(find_all(k, of_type=Placemark)):
        coords = p.geometry.coords[0]
        waypoints.append(
            COT(
                callsign=p.name if p.name else "Unnamed Waypoint",
                lon=coords[0],
                lat=coords[1],
                remarks=p.description if p.description else ""
            )
        )

    return waypoints


def _read_shelters(csv_path: str) -> list[COT]:
    shelters = []
    with open(csv_path, 'r') as f:
        csv_reader = csv.DictReader(f, delimiter=',')
        header_row = True
        for row in csv_reader:
            if header_row:
                # skip header
                header_row = False
                continue

            if row["Rodzaj obi"] == "[1] - (S) - schron":
                shelters.append(
                    COT(callsign="Schron", lon=row["x"], lat=row["y"], remarks=row["Adres"]))

    return shelters

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--schrony",
        type=str,
        help="Path of CSV file with Schrony data to convert",
    )
    group.add_argument(
        "--kml",
        type=str,
        help="Path of KML file to convert",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=True,
        help="Output file name",
    )
    args = parser.parse_args()

    cots = []
    if args.kml:
        cots = _convert_kml(args.kml)
    elif args.schrony:
        cots = _read_shelters('schrony-csv.csv')

    if not cots:
        return

    create_package(args.output, cots)


if __name__ == "__main__":
    main()
