from uuid import uuid4
from time import time
from datetime import date
from pathlib import Path
import shutil
import os

PACKAGE_NAME = "aaTest"
OUTPUT_PATH = "out"
UUID = uuid4()


class COT:
    def __init__(self, callsign: str, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        self.callsign = callsign
        self.uuid = str(uuid4()).upper()
        self.time = date.fromtimestamp(time()).strftime("%Y-%m-%dT00:00:00Z")
        self.type = "a-u-G"
        self.how = "h-g-i-g-o"
        self.icon_path = "COT_MAPPING_2525B/a-u/a-u-G"


def indent_write(f, txt, indent=0):
    f.write(f'{' ' * 2 * indent}{txt}\n')


def create_manifest(package_name: str, cots: list[COT]):

    output_path = Path(OUTPUT_PATH, 'manifest')
    output_path.mkdir()
    manifest_path = Path(output_path, 'manifest.xml')

    with open(manifest_path, 'w') as f:
        indent_write(f, '<?xml version="1.0" encoding="UTF-8"?>')
        indent_write(f, '<MissionPackageManifest version="2">')
        indent_write(f, '<Configuration>', 1)
        indent_write(f, f'<Parameter name="name" value="{package_name}">', 2)
        indent_write(
            f, f'<Parameter name="uid" value="{str(uuid4()).upper()}">', 2)
        indent_write(f, '<Parameter name="remarks" value="">', 2)
        indent_write(f, '</Configuration>', 1)
        indent_write(f, '<Contents>', 1)
        for cot in cots:
            indent_write(
                f, f'<Content zipEntry="{cot.uuid}/{cot.uuid}.cot" ignore="false">', 2)
            indent_write(f, f'<Parameter name="uid", value="{cot.uuid}"/>', 3)
            indent_write(f, '</Content>', 2)
        indent_write(f, '</Contents>', 1)
        indent_write(f, '</MissionPackageManifest>')


def create_cot(cot: COT):
    output_path = Path(OUTPUT_PATH, cot.uuid)
    output_path.mkdir()
    cot_path = Path(output_path, f'{cot.uuid}.cot')

    with open(cot_path, 'w') as f:
        indent_write(
            f, f'<event version="2.0" uid="{cot.uuid}" type="{cot.type}" how="{cot.how}" time="{cot.time}" start="{cot.time}" stale="{cot.time}">')
        indent_write(
            f, f'<point lat="{cot.lat}" lon="{cot.lon}" hae="0.0" ce="0.0" le="0.0" />')
        indent_write(f, '<detail>')
        indent_write(f, f'<contact callsign="{cot.callsign}"/>')
        indent_write(f, '<precisionlocation geopointsrc="???" altsrc="???"/>')
        indent_write(f, '<status readiness="true"/>')
        indent_write(f, '<archive/>')
        indent_write(
            f, f'<link uid="{UUID}" production_time="{cot.time}" type="a-f-G-U-C" parent_callsign="ATAK Marker Import" relation="p-p"/>')
        indent_write(f, f'<usericon iconsetpath="{cot.icon_path}"/>')
        indent_write(f, '<color argb="-1"/>')
        indent_write(
            f, '<_flow-tags_ TAK-Server-fe3bcbd8="2020-02-06T17:53:28Z"/>')
        indent_write(f, '<remarks></remarks>')
        indent_write(f, '')
        indent_write(f, '</detail>')
        indent_write(f, '</event>')


def create_package(name: str, cots: list[COT]):
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
    os.mkdir(OUTPUT_PATH)

    create_manifest(name, cots)
    for cot in cots:
        create_cot(cot)

    shutil.make_archive(name, "zip", root_dir="out")


cots = [
    COT("Test.1", "54.60902595027931", "18.01429596699901"),
    COT("Test.2", "54.60902595027931", "18.01429596699901"),
]
create_package(PACKAGE_NAME, cots)
