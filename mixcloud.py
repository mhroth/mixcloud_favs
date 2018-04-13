# Copyright 2018 Martin Roth (mhroth@gmail.com).
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.

import argparse
import datetime
import jinja2
import requests

# cli parser
parser = argparse.ArgumentParser(
    description="Runs the Heavy Royal web application.")
parser.add_argument(
        "username",
        help="Your mixcloud username.")
args = parser.parse_args()

r = requests.get("https://api.mixcloud.com/{0}/favorites/?limit=100".format(args.username))
r_json = r.json()
fav_list = r_json["data"]

while "next" in r_json["paging"]:
    r = requests.get(r_json["paging"]["next"])
    r_json = r.json()
    fav_list.extend(r_json["data"])

def filter_duration(duration_sec):
    d_min = int(int(duration_sec) / 60)
    if d_min < 60:
        return "{0}m".format(d_min)
    else:
        d_hour = int(d_min / 60)
        d_min = d_min % 60
        return "{0}h {1}m".format(d_hour, d_min)

def filter_created_time(created_time_str):
    created_time = datetime.datetime.strptime(created_time_str, "%Y-%m-%dT%H:%M:%SZ")
    return "{0}.{1:02}".format(created_time.year, created_time.month)

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))
env.filters['duration'] = filter_duration
env.filters['created_time'] = filter_created_time
template = env.get_template('template.html')

with open("./mixcloud.html", "w") as f:
    f.write(template.render(
        username=args.username,
        fav_list=fav_list,
        date_time=datetime.datetime.now()))
