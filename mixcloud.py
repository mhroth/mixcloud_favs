# Copyright 2018-2020 Martin Roth (mhroth@gmail.com).
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
parser.add_argument(
        "--out",
        default="./mixcloud.html",
        help="Output Path.")
args = parser.parse_args()

# get mixcloud favourites
r_json = requests.get("https://api.mixcloud.com/{0}/favorites/?limit=100".format(args.username)).json()
fav_list_mc = r_json["data"]

while "next" in r_json["paging"]:
    r_json = requests.get(r_json["paging"]["next"]).json()
    fav_list_mc.extend(r_json["data"])

# get soundcloud favourites
r_json = requests.get("http://api.soundcloud.com/users/{0}/favorites?client_id=94c6f1416b187b88a9ffe11bbd2920f6&linked_partitioning=1".format(args.username)).json()
fav_list_sc = r_json["collection"]

while "next_href" in r_json:
    r_json = requests.get(r_json["next_href"]).json()
    fav_list_sc.extend(r_json["collection"])

def filter_duration(duration_sec):
    d_min = int(int(duration_sec) / 60)
    if d_min < 60:
        return "{0}m".format(d_min)
    else:
        d_hour = int(d_min / 60)
        d_min = d_min % 60
        return "{0}h {1}m".format(d_hour, d_min)

def filter_created_time_mc(created_time_str):
    """ Parse the Mixcloud-format date string.
    """
    created_time = datetime.datetime.strptime(created_time_str, "%Y-%m-%dT%H:%M:%SZ")
    return "{0}.{1:02}".format(created_time.year, created_time.month)

def filter_created_time_sc(created_time_str):
    """ Parse the Soundcloud-format date string.
        e.g. 2017/11/08 19:27:35 +0000
    """
    created_time = datetime.datetime.strptime(created_time_str, "%Y/%m/%d %H:%M:%S +0000")
    return "{0}.{1:02}".format(created_time.year, created_time.month)

env = jinja2.Environment(loader=jinja2.FileSystemLoader('./'))
env.filters['duration'] = filter_duration
env.filters['created_time'] = filter_created_time_mc
env.filters['created_time_sc'] = filter_created_time_sc
template = env.get_template('template.html')

with open(args.out, "w") as f:
    f.write(template.render(
        username=args.username,
        fav_list_mc=fav_list_mc,
        fav_list_sc=fav_list_sc,
        date_time=datetime.datetime.now()))
