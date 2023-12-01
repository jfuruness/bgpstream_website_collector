import bs4
from requests_cache import CachedSession


def get_tags(tag: str, url: str, session: CachedSession) -> list[bs4.element.Tag]:
    """Returns tags on a given page"""

    resp = session.get(url)
    resp.raise_for_status()
    soup = bs4.BeautifulSoup(resp.text, "html.parser")
    resp.close()
    return soup.find_all(tag)
