from html.parser import HTMLParser

import markdown

class HtmlHeadingParser(HTMLParser):
    inside_h1 = False
    h1_data = None

    def handle_starttag(self, tag, attrs):
        if self.h1_data is None and tag == "h1":
            self.inside_h1 = True

    def handle_data(self, data):
        if self.inside_h1:
            self.h1_data = data
            self.inside_h1 = False


def get_heading(md):
    # Parse the HTML file using our custom parser
    parser = HtmlHeadingParser()
    parser.feed(markdown.markdown(md))
    return parser.h1_data
