from bs4 import BeautifulSoup


class BeautifulSoupMiddleware(object):
    def __init__(self, crawler):
        super(BeautifulSoupMiddleware, self).__init__()

        self.parser = crawler.settings.get('BEAUTIFULSOUP_PARSER', "html.parser")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_response(self, request, response, spider):
        """Overridden process_response would "pipe" response.body through BeautifulSoup."""
        return response.replace(body=str(BeautifulSoup(response.body, self.parser)))
