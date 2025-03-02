## Usage

Install requirements using for example pip:
```
pip install -r requirements.txt
```

Run the script:

```
python apdc.py <arguments>
```

### Convert KML to COT

```
python apdc.py --kml <kml_file_path> --output <output_package_name>
```

Convert KML file to ATAK package. Currently only supports converting placemarks (waypoints).
Other features will be ignored.

### Convert Polish shelters data to COT

```
python apdc.py --schrony <csv_file_path> --output <output_package_name>
```

Converts CSV file with data about Polish shelters to ATAK package. CSV file can be obtained from:
https://strazpozarna.maps.arcgis.com/home/item.html?id=11f24814a7044207af61f61f65382aaf
