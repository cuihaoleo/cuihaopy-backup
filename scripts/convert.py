#!/usr/bin/env python3

import sys
import io
import re
import os
from bs4 import BeautifulSoup

def gen_md(soup, ul_level=0):
    writer = io.StringIO()

    for child in soup.children:
        if child.name is None:
            text = str(child)
            text = text.replace('|', '\|')
            text = text.replace('*', '\*')
            writer.write(text)
        elif child.name == "div":
            inner = gen_md(child)
            writer.write(inner + '\n')
        elif child.name == "p":
            inner = gen_md(child)
            writer.write(inner + '\n')
        elif child.name == "span":
            inner = gen_md(child)
            writer.write(inner)
        elif child.name == "strong":
            inner = gen_md(child)
            buf = []
            for line in inner.split('\n'):
                first = len(line) - len(line.lstrip())
                buf.append("%s**%s**" % (line[:first], line[first:]))
            writer.write("\n".join(buf))
        elif child.name == "em":
            inner = gen_md(child)
            buf = []
            for line in inner.split('\n'):
                first = len(line) - len(line.lstrip())
                buf.append("%s*%s*" % (line[:first], line[first:]))
            writer.write("\n".join(buf))
        elif child.name == "pre":
            lang = re.search("brush:\s*(\w+)", str(child)).group(1)
            writer.write("```%s\n%s\n```" % (lang, child.text))
        elif child.name in [ "h1", "h2", "h3", "h4", "h5", "h6" ]:
            level = int(child.name[1])
            inner = gen_md(child)
            writer.write("#" * level + ' ' + inner)
        elif child.name == "blockquote":
            inner = gen_md(child)
            buf = []
            for line in inner.split('\n'):
                buf.append("> " + line)
            writer.write("\n".join(buf))
        elif child.name == "ul":
            inner = gen_md(child, ul_level=ul_level+1)
            writer.write('\n' + inner + '\n')
        elif child.name == "li":
            inner = gen_md(child)
            writer.write('*' * ul_level + " " + inner + '\n')
        elif child.name == "table":
            table = []
            tbody = child.find_all("tbody")[0]

            for tr in tbody.children:
                if tr.name != "tr":
                    continue
                row = []
                for td in tr.children:
                    if td.name != "td":
                        continue
                    inner = gen_md(td)
                    inner = inner.replace('\n', ' ').strip()
                    row.append(inner)
                table.append(row)
            nrow = len(table)
            ncol = max(len(row) for row in table)
            writer.write('\n')
            for row in table:
                while len(row) < ncol:
                    row.append('')
                writer.write('| ' + ' | '.join(row) + ' |\n')
            writer.write('\n')
        elif child.name == "a":
            link = child["href"]
            inner = gen_md(child).replace('\n', ' ').strip()
            writer.write('[%s](%s)' % (inner, link))
        elif child.name == "img":
            link = child["src"]
            desc = child["alt"]
            writer.write('![%s](%s)' % (desc, link))
        elif child.name == "br":
            writer.write('\n')
        else:
            raise Exception("Unknown name: %s" % child.name)

    return writer.getvalue().strip()

with open(sys.argv[1]) as fin:
    soup = BeautifulSoup(fin, "lxml")

for elem in soup.find_all("div", class_="post"):
    title = elem.select("h2 a")[0].text
    date = elem.select("div.post_date")[0].text
    try:
        category = elem.select("div.postmetadata a")[0].text
    except IndexError:
        category = "Uncategorized"
    tags = [e.text for e in elem.select("p.tags a")]
    raw_content = elem.select("div.entry")[0]
    mon, day, year = date.split('/')
    date = "%04d-%02d-%02d" % (2000 + int(year), int(mon), int(day)) 
    print(title, date, category, tags)
    fname = os.path.join("posts", "%s-%s.md" % (date, title))

    front = "---\n" \
            "title: \"%s\"\n" \
            "date: %s\n" \
            "category: %s\n" \
            "tags: %s\n" \
            "layout: post\n" \
            "---\n" % (title, date, category, " ".join(tags))
    titleline = "## " + title
    md = gen_md(raw_content)

    with open(fname, "w") as fout:
        print(front, file=fout)
        #print("## " + title + '\n', file=fout)
        print(md, file=fout)
        
    #print(raw_content)
    #print(md)

# then run
# sed -i "s_https://web.archive.org/web/[^/]\+/__g" *.md
# to convert Internet Archive links back
