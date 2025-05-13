import unittest
from converter import text_node_to_html_node
from textnode import TextNode, TextType
from leafnode import LeafNode

class TestTextNodeToHtmlNode(unittest.TestCase):
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, None)
        self.assertEqual(html.value, "This is a text node")

    def test_bold(self):
        node = TextNode("Bold!", TextType.BOLD)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "b")
        self.assertEqual(html.value, "Bold!")

    def test_italic(self):
        node = TextNode("Italic", TextType.ITALIC)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "i")
        self.assertEqual(html.value, "Italic")

    def test_code(self):
        node = TextNode("print()", TextType.CODE)
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "code")
        self.assertEqual(html.value, "print()")

    def test_link(self):
        node = TextNode("Google", TextType.LINK, "https://google.com")
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "a")
        self.assertEqual(html.value, "Google")
        self.assertEqual(html.props["href"], "https://google.com")

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://example.com/image.png")
        html = text_node_to_html_node(node)
        self.assertEqual(html.tag, "img")
        self.assertEqual(html.value, "")
        self.assertEqual(html.props["src"], "https://example.com/image.png")
        self.assertEqual(html.props["alt"], "Alt text")

    def test_unsupported_type(self):
        class FakeType:
            pass
        with self.assertRaises(ValueError):
            text_node_to_html_node(TextNode("Fake", FakeType))

if __name__ == "__main__":
    unittest.main()