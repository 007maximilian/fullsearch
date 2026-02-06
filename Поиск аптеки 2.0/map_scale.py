def calculate_scale_params(toponym):
    envelope = toponym["boundedBy"]["Envelope"]
    lower_corner = envelope["lowerCorner"].split()
    upper_corner = envelope["upperCorner"].split()
    
    lower_longitude, lower_latitude = float(lower_corner[0]), float(lower_corner[1])
    upper_longitude, upper_latitude = float(upper_corner[0]), float(upper_corner[1])
    
    longitude_span = abs(upper_longitude - lower_longitude)
    latitude_span = abs(upper_latitude - lower_latitude)
    
    spn_longitude = str(longitude_span)
    spn_latitude = str(latitude_span)
    
    return spn_longitude, spn_latitude