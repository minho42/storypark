import json
import shutil
from pathlib import Path

import requests

from utils import timeit

filename = "output.txt"
data = []


def save_image_to_file(name, src):
    res = requests.get(src, stream=True)
    if not res.ok:
        print(f"request failed: {name}")
        return False
    try:
        with open(name, "wb") as file:
            shutil.copyfileobj(res.raw, file)
    except:
        print(f"saving failed: {name}")
        return False
    return True


# {"post_url": "https://app.storypark.com/activity/?post_id=56882803",
# "name": "date__title__1.jpeg",
# "src": "..."},

with open(filename, "r") as file:
    data = file.readlines()

print(len(data))

data = [json.loads(row.strip()) for row in data]

outdir = Path("./download")


@timeit
def download():
    post_url_to_restart_from = ""

    count = 0
    for index, row in enumerate(data):
        if post_url_to_restart_from:
            print(f"skipping {row['post_url']} until post_url: {post_url_to_restart_from}")
            if row["post_url"] == post_url_to_restart_from:
                post_url_to_restart_from = ""
            else:
                continue

        filename = (outdir / row["name"]).resolve()
        if filename.exists():
            continue
        r = save_image_to_file(name=filename, src=row["src"])
        if r:
            count += 1
        print(index + 1, row["name"])
    print(f"{count}/{len(data)} images downloaded")


download()
