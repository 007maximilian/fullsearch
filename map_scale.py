def get_map_params(toponym):
    envelope = toponym["boundedBy"]["Envelope"]
    lower_corner = envelope["lowerCorner"].split()
    upper_corner = envelope["upperCorner"].split()
    
    lower_longitude, lower_latitude = map(float, lower_corner)
    upper_longitude, upper_latitude = map(float, upper_corner)
    
    longitude_span = abs(upper_longitude - lower_longitude)
    latitude_span = abs(upper_latitude - lower_latitude)
    
    center_longitude = (lower_longitude + upper_longitude) / 2
    center_latitude = (lower_latitude + upper_latitude) / 2
    
    return {
        "ll": f"{center_longitude},{center_latitude}",
        "spn": f"{longitude_span},{latitude_span}"
    }