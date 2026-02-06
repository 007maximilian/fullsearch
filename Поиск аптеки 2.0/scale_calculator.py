def calculate_spn_for_two_points(point1, point2):
    lon1, lat1 = point1
    lon2, lat2 = point2
    
    lon_span = abs(lon1 - lon2) * 1.5
    lat_span = abs(lat1 - lat2) * 1.5
    
    min_span = 0.001
    lon_span = max(lon_span, min_span)
    lat_span = max(lat_span, min_span)
    
    return str(lon_span), str(lat_span)

def calculate_center_for_two_points(point1, point2):
    lon1, lat1 = point1
    lon2, lat2 = point2
    
    center_lon = (lon1 + lon2) / 2
    center_lat = (lat1 + lat2) / 2
    
    return str(center_lon), str(center_lat)