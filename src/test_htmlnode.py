import unittest
from htmlnode import HTMLNode

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_single(self):
        node = HTMLNode(tag="a", props={"href": "https://example.com"})
        self.assertEqual(node.props_to_html(), ' href="https://example.com"')

    def test_props_to_html_multiple(self):
        node = HTMLNode(tag="a", props={
            "href": "https://example.com",
            "target": "_blank"
        })
        self.assertEqual(
            node.props_to_html(),
            ' href="https://example.com" target="_blank"'
        )

    def test_repr(self):
        node = HTMLNode(tag="p", value="Hello", props={"class": "text"})
        expected = (
            "HTMLNode(tag='p', value='Hello', children=[], props={'class': 'text'})"
        )
        self.assertEqual(repr(node), expected)

if __name__ == "__main__":
    unittest.main()