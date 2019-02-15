from shapely.geometry import Point, LineString
import geopandas as gpd

def transform_shape_to_lines(shapes):
    """Transform gtfs shapes to lines."""
    shapes['coords'] = tuple(zip(shapes['shape_pt_lon'], shapes['shape_pt_lat']))
    shapes = shapes.sort_values(by=['shape_id', 'shape_pt_sequence'])

    line_lists = shapes.groupby('shape_id').agg({'shape_id': 'first', 'shape_dist_traveled': 'sum', 'coords': lambda c: (c.tolist())})

    line_lists['coords'] = line_lists['coords'].apply(LineString)
    gtfs_shapes = gpd.GeoDataFrame(line_lists, geometry='coords')
    gtfs_shapes.crs = {'init' :'epsg:4326'}

    return gtfs_shapes
    
def transform_stops_to_points(stops):
    stops['geometry'] = list(zip(stops['stop_lon'], stops['stop_lat']))
    stops['geometry'] = stops['geometry'].apply(Point)
    stops.set_index('stop_id', inplace=True)
    stops['stop_id'] = stops.index
    stop_points = gpd.GeoDataFrame(stops, geometry='geometry')
    
    return stop_points

def transform_xy_to_points(df, x_col, y_col, index=None):
    df['geometry'] = list(zip(df[x_col], df[y_col]))
    df['geometry'] = df['geometry'].apply(Point)
    if index:
        df.set_index(index, inplace=True)
        df[index] = df.index
    stop_points = gpd.GeoDataFrame(df, geometry='geometry')
    
    return stop_points