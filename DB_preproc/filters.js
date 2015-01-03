HIGHWAY_LIST = ["motorway", 
				"trunk", 
				"primary", 
				"secondary",
				"tertiary",
				"unclassified",
				"residential",
				"motorway_link",
				"trunk_link",
				"primary_link",
				"secondary_link",
				"tertiary_link",
				"bus_guideway",
				"road",
				"footway",
				"cycleway",
				"steps",
				"path",
				"bus_stop"];

/*
	Strangely, public transports are not available on city maps.
	We will use GTFS.
PUBLIC_TRANSPORT_LIST = ["stop_position",
						 "platform",
						 "station",
						 "stop_area"];
*/

ROUTE_LIST = ["bicycle",
			  "bus",
		 	  "ferry",
		 	  "railway",
		 	  "train",
		 	  "tram"];


RAILWAY_LIST = ["light_rail",
		   		"monorail",
		   		"rail",
		   		"subway",
		   		"tram",
		   		"subway_entrance",
		   		"station",
		   		"tram_stop",
		   		"halt"];


conn = new Mongo();
db = conn.getDB("tempOSM");
print("Connected to tempOSM database");

newdb = conn.getDB("filteredOSM");
print("Connected to new database");

newdb.dropDatabase();

/*
	Searching for highways
*/
print("Filtering highways...")
/*
	In points collection
*/
//	Querying
print("\tQuerying points for highways...");
cursor = db.points.find({
	"properties.highway" : {$in: HIGHWAY_LIST}
});
print("\tDone querying points for highways, inserting...");
//	Inserting
newdb.highways.insert(cursor.toArray());
print("\tDone inserting points for highways");
/*
	In lines collection
*/
// Querying
print("\tQuerying lines for highways...");
cursor = db.lines.find({
	"properties.highway" : {$in: HIGHWAY_LIST}
});
print("\tDone querying lines for highways, inserting...");
// Inserting
newdb.highways.insert(cursor.toArray());
print("\tDone inserting lines for highways");
//
print("Done filtering highways.");

/*
	Searching for routes
*/
print("Filtering routes...")
/*
	In points collection
*/
//	Querying
print("\tQuerying points for routes...");
cursor = db.points.find({
	"properties.route" : {$in: ROUTE_LIST}
});
print("\tDone querying points for routes, inserting...");
//	Inserting
newdb.routes.insert(cursor.toArray());
print("\tDone inserting points for routes");
/*
	In lines collection
*/
// Querying
print("\tQuerying lines for routes...");
cursor = db.lines.find({
	"properties.route" : {$in: ROUTE_LIST}
});
print("\tDone querying lines for routes, inserting...");
// Inserting
newdb.routes.insert(cursor.toArray());
print("\tDone inserting lines for routes");
//
print("Done filtering routes.");


/*
	Searching for railways
*/
print("Filtering railways...")
/*
	In points collection
*/
//	Querying
print("\tQuerying points for railways...");
cursor = db.points.find({
	"properties.railway" : {$in: RAILWAY_LIST}
});
print("\tDone querying points for railways, inserting...");
//	Inserting
newdb.railways.insert(cursor.toArray());
print("\tDone inserting points for railways");
/*
	In lines collection
*/
// Querying
print("\tQuerying lines for railways...");
cursor = db.lines.find({
	"properties.railway" : {$in: RAILWAY_LIST}
});
print("\tDone querying lines for railways, inserting...");
// Inserting
newdb.railways.insert(cursor.toArray());
print("\tDone inserting lines for railways");
//
print("Done filtering routes.");

/*
	Geoindexing
*/
print("Geoindexing highways");
newdb.highways.ensureIndex({"geometry : 2dsphere"});
print("Geoindexing routes");
newdb.routes.ensureIndex({"geometry : 2dsphere"});
print("Geoindexing railways");
newdb.railways.ensureIndex({"geometry : 2dsphere"});
print("Done geoindexing");

db.dropDatabase();
print("Done.")



/*
db.lines.find(
   {
     geometry:
       { $geoNear :
          {
            $geometry: { type: "Point",  coordinates: [ -123.4568374, 38.7139953 ] },
            $minDistance: 1000,
            $maxDistance: 5000
          }
       }
   }
)
*/

//db.lines.ensureIndex({geometry : "2dsphere"});

