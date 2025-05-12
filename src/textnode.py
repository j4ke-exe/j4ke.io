from enum import Enum

class TextType(Enum):
	TEXT = "text"		# normal text
	BOLD = "bold"		# _bold text_
	ITALIC = "italic"	# _italic text_
	CODE = "code"		# `code text`
	LINK = "link"		# [anchor text](url)
	IMAGE = "image"		# ![alt text](url)

class TextNode:
	def __init__(self, text, text_type, url=None):
		self.text = text
		self.text_type = text_type
		self.url = url

	def __eq__(self, other):
		return (
			isinstance(other, TextNode) and
			self.text == other.text and
			self.text_type == other.text_type and
			self.url == other.url
		)

	def __repr__(self):
		return f"TextNode({self.text}, {self.text_type.value}, {self.url})"