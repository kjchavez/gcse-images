import os
import cPickle
import cStringIO
import requests

# Get API key and search engine id from environment variables
api_key = os.environ['GOOGLE_API_KEY']
search_engine_id = os.environ["GOOGLE_CSE_ID"]

cache_directory = "/tmp/gimage/cache"


def get_valid_filename(string):
    return ''.join(ch for ch in string if ch.isalnum())


# To help alleviate the problem with a small query limit, we will cache all
# results to minimize impact while developing/testing.
def compute_cache_key(query):
    key = query.replace(' ', '') + ".search"
    return key


def get_cache_entry(query):
    if not os.path.isdir(cache_directory):
        return None

    key = compute_cache_key(query)
    filename = os.path.join(cache_directory, key)
    if os.path.exists(filename):
        with open(filename) as fp:
            return cPickle.load(fp)


def save_cache_entry(query, results):
    if not os.path.isdir(cache_directory):
        os.makedirs(cache_directory)
    key = compute_cache_key(query)
    filename = os.path.join(cache_directory, key)
    with open(filename, 'w') as fp:
        cPickle.dump(results, fp)


def search_images(query, filetype=None):
    """ Issues a Google Image search for the given query.

    Args:
        query:  a raw string query
        filetype:  (optional) a file extension to filter the search, e.g. .jpg

    Returns:
        A dictionary of search results, including:

            items - the list of search results
    """
    results = get_cache_entry(query)
    if results is not None:
        return results

    # Otherwise, we'll issue the search.
    search_url = "https://www.googleapis.com/customsearch/v1?" \
                 "key=%s&cx=%s&q=%s&searchType=image" % \
                 (api_key, search_engine_id, query)

    if filetype is not None:
        search_url += "&fileType=%s" % filetype

    results = requests.get(search_url)

    # And cache the results.
    save_cache_entry(query, results.json())
    return results.json()


def download_and_save_image(item, filename):
    """ Saves a search result item with for an image to a file.

    Args:
        item:  a search result item as returned by the Google Custom Search API
        filename:  base of a filename to save the image to. This should not
                   include the extension (e.g. .jpg). The extension will be
                   determined by the mime of the result.
    """
    image = requests.get(item['link'])
    if 'image' not in item['mime']:
        print "Search result is not an image."
        return None

    ext = item['mime'].split('/')[-1]
    filename += '.' + ext

    with open(filename, 'wb') as fp:
        fp.write(image.content)


def search_and_save_first_result(queries, filetype=None, directory="./"):
    """ Saves the first result for each query in a list of queries.

    Args:
        queries: a list of queries to issue
        filetype: a file extensions (e.g. 'png') to use as a filter.
        directory: a directory to save all the images to.
    """
    if not os.path.isdir(directory):
        os.makedirs(directory)

    for query in queries:
        results = search_images(query, filetype=filetype)
        filename = os.path.join(directory, get_valid_filename(query))
        download_and_save_image(results['items'][0], filename)
