mongo tempOSM --eval "db.dropDatabase()"

mongoimport -d tempOSM -c points --file san-francisco-bay_california.osm-point.geojson
mongoimport -d tempOSM -c lines --file san-francisco-bay_california.osm-line.geojson
mongoimport -d tempOSM -c polygons --file san-francisco-bay_california.osm-polygon.geojson

