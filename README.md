# Google Custom Search Engine, Images
This is a lightweight wrapper over the Google Custom Search API to facilitate
image searches.

To use, make sure to set the following environment variables:

* `GOOGLE_API_KEY`: Your Google developer API key (a server key).
* `GOOGLE_CSE_ID`:  The id of the Custom Search Engine you set up in your developer
                console.

Then you may do

```python
import gimage

results = gimage.search_images('ostrich')
for i, item in enumerate(results['items']):
    gimage.download_and_save_image(item, 'ostrich-%03d' % i)
```

This will save the first page of image results as files named ostrich-001,
ostrich-002, etc. Extensions are determined by the mime of the result.
