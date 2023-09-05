import requests
from selectolax.parser import HTMLParser, Node
from ..utils import get_attribute, get_text

class BaseMangaScraper:
    def __init__(self, url: str) -> None:
        self.url = url
        # get parser
        self.parser = self.__get_parser()

    def __get_parser(self) -> HTMLParser:
        res = requests.get(self.url)
        return HTMLParser(res.content)

    def __get_slug(self, node: Node) -> str | None:
        slug_string = get_attribute(node, "#ani_detail .ani_detail-stage .anis-content .anisc-detail .manga-buttons a", "href")
        return slug_string.split("/")[-1] if slug_string else None

    def __get_id(self, node: Node) -> str | None:
        slug = self.__get_slug(node)
        return slug.split("-")[-1] if slug else None

    def __get_genres(self, node: Node) -> list | None:
        genres = node.css(".anisc-detail .sort-desc .genres a")
        return [genre.text() for genre in genres] if genres else None

    def __get_authers(self, node: Node) -> list | None:
        authers = node.css(".anisc-detail .anisc-info .item:nth-child(3) a")
        return [auther.text() for auther in authers] if authers else None

    def __get_magazines(self, node: Node) -> list | None:
        magazines = node.css(".anisc-detail .anisc-info .item:nth-child(4) a")
        return [magazine.text() for magazine in magazines] if magazines else None

    def __get_published(self, node: Node) -> str | None:
        published_string = get_text(node, ".anisc-detail .anisc-info .item:nth-child(5) .name")
        return published_string.split(" to ")[0] if published_string else None

    def __get_views(self, node: Node) -> str | None:
        views_string = get_text(node, ".anisc-detail .anisc-info .item:nth-child(7) .name")
        return views_string.replace(",", "") if views_string else None

    def __get_chapters_volumes(self, type: str) -> list | None:
        items = self.parser.css(f"#main-content #list-{type} .dropdown-menu a")

        item_list = []
        for item in items:
            text = item.text().translate(str.maketrans("", "", "[]()"))

            item_dict = {
                "total": text.split()[2],
                "lang": text.split()[0]
            }

            item_list.append(item_dict)
        return item_list if item_list else None

    def build_dict(self, node: Node) -> dict:
        manga_dict = {
            "manga_id": self.__get_id(node),
            "title": get_text(node, ".anisc-detail .manga-name"),
            "alt_title": get_text(node, ".anisc-detail .manga-name-or"),
            "slug": self.__get_slug(node),
            "type": get_text(node, ".anisc-detail .anisc-info .item:nth-child(1) a"),
            "status": get_text(node, ".anisc-detail .anisc-info .item:nth-child(2) .name"),
            "published": self.__get_published(node),
            "score": get_text(node, ".anisc-detail .anisc-info .item:nth-child(6) .name"),
            "views": self.__get_views(node),
            "cover": get_attribute(node, ".anisc-poster .manga-poster-img", "src"),
            "synopsis": get_text(node, ".anisc-detail .sort-desc .description"),
            "genres": self.__get_genres(node),
            "authers": self.__get_authers(node),
            "mangazines": self.__get_magazines(node),
            "chapters": self.__get_chapters_volumes("chapter"),
            "volumes": self.__get_chapters_volumes("vol")
        }

        return manga_dict