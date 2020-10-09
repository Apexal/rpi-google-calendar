import redis
import json

r = redis.Redis()


def get_section(semester, crn: str):
    raw_section = r.hget(f'{semester}:sections', crn)
    if raw_section is None:
        return None

    section = json.loads(r.hget(f'{semester}:sections', crn))

    # TODO: do this in parse library
    for key in ['courseTitle', 'courseSubjectPrefix', 'courseSubjectCode']:
        section[key] = section['periods'][0][key]

    return section
