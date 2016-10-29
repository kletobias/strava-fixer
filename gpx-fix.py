from gpxpy import parse
import datetime
from copy import deepcopy

f = open('track.gpx', 'r')
gpx = parse(f)


for track in gpx.tracks:
    for segment in track.segments:
        for i, point in enumerate(segment.points):
            prev = segment.points[i-1]

            if i > 0 and point.time - prev.time > datetime.timedelta(minutes=5):
                print("Found gap of {}".format(point.time - prev.time))
                print(segment.points[i-1], segment.points[i], i)
                # Now that we've found the splice point, we need to find 2 points
                # in the future that correspond in reverse order
                # (Ie, you rode back along the path you came.)

                start = segment.points[i-1]
                end = segment.points[i]

                candidate_start = []
                candidate_end = []

                for j, p2 in enumerate(segment.points[i+1:], i + 1):
                    if p2.distance_2d(end) < 10:
                        candidate_start.append((p2, j))

                    if p2.distance_2d(start) < 10:
                        candidate_end.append((p2, j))                        
            
                print("Candidates for start point:")
                for k, (p, j) in enumerate(candidate_start):
                    print('[{}]: {}'.format(k, p))

                opt = input("Choice? ")
                new_start = candidate_start[int(opt)]

                print("Candidates for end point:")
                for k, (p, j) in enumerate(candidate_end):
                    print('[{}]: {}'.format(k, p))

                opt = input("Choice? ")
                new_end = candidate_end[int(opt)]

                # We need to copy all those points and splice them between start
                # and end.
                new_points = list(reversed(deepcopy(segment.points[new_start[1]:new_end[1]+1])))

                # We need to interpolate the times on each of the points.
                # We know the start/end, just need to work out how many points
                # we have, and then re-write all the times.

                delta_per_point = (end.time - start.time) / len(new_points)
                curr_time = start.time

                # Re-write all the points
                for p in new_points:
                    p.time = curr_time
                    curr_time = curr_time + delta_per_point

                # Need to splice these back into the segment points array.

                before = segment.points[:i]
                after = segment.points[i:]

                segment.points = before + new_points + after

                f = open('output.gpx', 'w')
                f.write(gpx.to_xml())
                exit(0)

            # print('Point at ({0},{1}) -> {2}'.format( point.latitude, point.longitude, point.elevation ))
