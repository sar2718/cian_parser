def generate_price_ranges(limits):
    if not limits:
        return [{"min": None, "max": None}]
    
    sorted_limits = sorted(limits)
    ranges = [{"min": None, "max": sorted_limits[0]}]

    for i in range(1, len(sorted_limits)):
        ranges.append({"min": sorted_limits[i-1], "max": sorted_limits[i]})

    ranges.append({"min": sorted_limits[-1], "max": None})
    return ranges


def build_url(base_url, price_range):
    url = base_url
    if price_range["min"] is not None:
        url += f"&minprice={price_range['min']}"
    if price_range["max"] is not None:
        url += f"&maxprice={price_range['max']}"
    return url
