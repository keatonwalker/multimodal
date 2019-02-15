import arcpy
import pandas as pd
import os

def buffer_bike_lanes(existing_regional_lanes, merge_fields, working_data_gdb, bikelane_buffer_dist=4):
    # Buffer bike lanes and merge buffer by Status and Type
    wfrc_bike_buffer = os.path.join(working_data_gdb, 'wfrc_bike_buffer')
    arcpy.analysis.Buffer(
        existing_regional_lanes,
        wfrc_bike_buffer,
        '{} Meters'.format(bikelane_buffer_dist),
        'FULL',
        'ROUND',
        'LIST',
        ';'.join(merge_fields),
        'PLANAR')
    
    return wfrc_bike_buffer


def join_roads_to_bike_buffer(roads, wfrc_bike_buffer, working_data_gdb):
        # Find all roads within a bike lane buffer
    wrfc_buffer_roads_join = os.path.join(working_data_gdb, 'wfrc_buffer_roads_join')
    arcpy.analysis.SpatialJoin(
        roads,
        wfrc_bike_buffer,
        wrfc_buffer_roads_join,
        join_operation="JOIN_ONE_TO_ONE",
        join_type="KEEP_COMMON",
        match_option="WITHIN")
    
    return wrfc_buffer_roads_join

def arcgis_to_pandas(cursor):
    """
        Load data into a Pandas Data Frame for subsequent analysis.
        :param table: Table readable by ArcGIS.
        :param field_names: List of fields.
        :return: Pandas DataFrame object.
    """
    field_names = cursor.fields
    # create a pandas data frame
    dataframe = pd.DataFrame(columns=field_names)

    for row in cursor:
        # combine the field names and row items together, and append them
        dataframe = dataframe.append(
            dict(zip(field_names, row)), 
            ignore_index=True
        )
    # return the pandas data frame
    return dataframe


def get_unique_lane_types(wrfc_buffer_roads_join, lane_type_field, working_data_gdb):
    """ Get unique bike lane types from WFRC data"""
    bike_lane_type_freq = os.path.join(working_data_gdb, 'wfrc_bike_lane_types')
    arcpy.analysis.Frequency(
        wrfc_buffer_roads_join,
        bike_lane_type_freq,
        lane_type_field)
    lane_types = []
    dataframe = None
    with arcpy.da.SearchCursor(bike_lane_type_freq, [lane_type_field]) as cursor:
        dataframe = arcgis_to_pandas(cursor)
    
    return (lane_types, dataframe)




if __name__ == '__main__':

    wfrc_bike_lanes = r'C:\giswork\multimodal\bikelanes\SourceData.gdb\Bike_Network_WFRC'
    existing_status_field = 'Status'
    network_field = 'Network'
    lane_type_field = 'Type'
    
    roads = r'C:\Users\kwalker\Documents\ArcGIS\Projects\MultiModal bike lanes\UTRANS.agrc.utah.gov.sde\UTRANS.TRANSADMIN.Roads_Edit'
    
    working_dir = r'C:\giswork\multimodal\bikelanes'
    working_data_gdb_name = r'WorkingData.gdb'
    working_data_gdb = os.path.join(working_dir, working_data_gdb_name)

    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    if arcpy.Exists(working_data_gdb):
        arcpy.management.Delete(working_data_gdb)
    
    arcpy.management.CreateFileGDB(working_dir, working_data_gdb_name)

    # Select Regional and exitisting bike lanes
    if arcpy.Exists('existing_regional'):
        arcpy.Delete('existing_regional')
    existing_regional_lanes = arcpy.management.MakeFeatureLayer(
        wfrc_bike_lanes,
        'existing_regional',
        """{} = 'Regional' And {} = 'Existing'""".format(network_field, existing_status_field))[0]
    
    # Buffer bike lanes and merge buffer by Status and Type
    bikelane_buffer_dist = 4
    merge_fields = [existing_status_field, lane_type_field]
    wfrc_bike_buffer = buffer_bike_lanes(existing_regional_lanes, merge_fields, bikelane_buffer_dist)

    # Find all roads within a bike lane buffer
    wrfc_buffer_roads_join = join_roads_to_bike_buffer(roads, wfrc_bike_buffer)
    
    dataframe = get_unique_lane_types(wrfc_buffer_roads_join, lane_type_field, working_data_gdb)
    
    print(dataframe)