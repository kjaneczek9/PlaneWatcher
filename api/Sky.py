"""
Sky object, made up of planes.
Aka an intro to object oriented class example that you'd through you'd never use
probably.
"""
class Sky:
    def __init__(self):
        # All planes from our antenna.
        self.planes = []

        # Planes filtered out that we're pretty sure are taking off.
        self.planes_to_show = []

        # Keep a list of hex codes so we can identify planes.  
        self.current_hex_codes = []

    def process_plane(self, plane_to_process):
        # Case #1 - brand new plane.
        if plane_to_process.hex_code not in self.current_hex_codes and plane_to_process.last_seen < 20:
            self.planes.append(plane_to_process)
            self.current_hex_codes.append(plane_to_process.hex_code)

        # Case #2 - we already have this plane.
        if plane_to_process.hex_code in self.current_hex_codes:
            # Find its index.
            idx = self.current_hex_codes.index(plane_to_process.hex_code)

            # If stale, remove this.
            if plane_to_process.last_seen > 20:
                del self.planes[idx]
                del self.current_hex_codes[idx]
                return

            # Update the plane.
            self.planes[idx].update(plane_to_process)

        # Go through all of our updated planes and determine what should be shown.
        to_show = []
        for plane in self.planes:
            if plane.safe_to_show():
                plane.prepare_to_show()
                to_show.append(plane)
        self.planes_to_show = to_show

