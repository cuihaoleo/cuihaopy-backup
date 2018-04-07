#!/bin/bash
rm -f posts/*
ln -snf ../_posts posts
ls *.html | xargs -I{} python3 convert.py {}
sed -i "s_https://web.archive.org/web/[^/]\+/__g" posts/*.md
