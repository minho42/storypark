# Storypark

Download images from storypark website using Python and Chrome Selenium

> Update
> 
> Turns out there is such a function from the website already:
> 
> Menu -> Edit next to [Child name] -> Export portfolio


## Collect data

```python
python 1.collector.py
```

### Post URLs to visit

post_urls.txt
```text
https://app.storypark.com/activity/?post_id=1
https://app.storypark.com/activity/?post_id=2
```

### Image links

output.txt
```text
{
    "post_url": "https://app.storypark.com/activity/?post_id=1", 
    "name": "15th_september_2020_sea_creatures_15_09_20_17.jpeg", 
    "src": "https://d1f34qwh8rni3t.cloudfront.net/media/..."
}, 
```

## Save images

```python
python 2.downloader.py
```

## Limitations
- Videos are not saved
  - Video only pages were ignored, but there could be some videos that were missed among other images
- Multiple steps to get the job done
- Super slow, takes really long time
  - `python 1.collector.py` only took more than 3 hours to run 😳
  - `time.sleep(n)` were used generously to prevent exceptions
  - `python 2.downloader.py` only took more than 1 hour to run 😳
