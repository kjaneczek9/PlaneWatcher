# Regex to find the html string that defines the destination :,)
AIRNAV_RADARBOX_DESTINATION_REGEX = r"to\s+([^\.,]+(?:, [A-Z]{2})?)"

# We regex for City, State, which isnt how international destinations show up (Country only)
# An international dest would have this in its query which gives it away
AIRNAV_RADARBOX_INTERNATIONAL_COND = 'on AirNav RadarBox"/>'

# Latitude of close runway
CLOSE_LATITUDE = 33.95

# Latitude of far runway (theres 2 b/c its right on the border)
FAR_LATITUDE = [33.93, 33.94]