from textnode import TextNode, TextType

def main():
	result = TextNode("This is some anchor text", TextType.LINK, "https://j4ke.io")
	print(result)

if __name__ == "__main__":
	main()