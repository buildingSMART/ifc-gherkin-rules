import markdown
import pdfkit

with open("README.md", "r") as file:
    md_content = file.read()

html_content = markdown.markdown(md_content)

with open("README.html", "w") as file:
    file.write(html_content)

pdfkit.from_file("README.html", "README.pdf")