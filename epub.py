import os
import os.path
import zipfile
import shutil
import ssl
import urllib.request
import urllib.parse
import uuid
from bs4 import BeautifulSoup

def makechapter(chapter_title,content,file_name_out):
    if os.path.exists(file_name_out):
        return False
    soup = BeautifulSoup(content, "lxml")

    new_h1 = soup.new_tag("h1")
    new_h1.string = chapter_title
    soup.body.insert(0,new_h1)

    new_head = soup.new_tag("head")
    soup.html.insert(0,new_head)

    new_title = soup.new_tag("title")
    new_title.string = chapter_title
    soup.html.head.insert(0,new_title)

    soup.html["xmlns"] = "http://www.w3.org/1999/xhtml"

    for match in soup.findAll('span'):
        match.unwrap()

    for match in soup.findAll('a'):
        match.unwrap()

    #for p in soup.find_all('p'):
    #    p.attrs= {}


    file = open(file_name_out, "w", encoding = "utf8")
    file.write(str(soup).replace("『","\"").replace("「","\"").replace("」","\"").replace("』","\"") )
    file.close()
    return file_name_out



def generate_epub(html_files, novelname, author,coverfile):
    if not os.path.exists("output"):
        os.makedirs("output")
    epub = zipfile.ZipFile(os.path.join("output",novelname)  + ".epub", "w")

    # The first file must be named "mimetype"
    epub.writestr("mimetype", "application/epub+zip")

     # The filenames of the HTML are listed in html_files
    # We need an index file, that lists all other HTML files
    # This index file itself is referenced in the META_INF/container.xml
    # file
    epub.writestr("META-INF/container.xml", '''<container version="1.0"
                  xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
          <rootfiles>
            <rootfile full-path="OEBPS/Content.opf" media-type="application/oebps-package+xml"/>
          </rootfiles>
        </container>''')

    # The index file is another XML file, living per convention
    # in OEBPS/Content.xml
    uniqueid = "urn:uuid:"+uuid.uuid1().hex
    index_tpl = '''<package version="3.1"
    xmlns="http://www.idpf.org/2007/opf" unique-identifier="''' + uniqueid + '''">
            <metadata>
                %(metadata)s
                <meta name="cover" content="cover1" />
            </metadata>
            <manifest>
                <item href="titlepage.xhtml" id="titlepage" media-type="application/xhtml+xml" properties="svg calibre:title-page"/>
                <item href="cover.jpg" id="cover1" media-type="image/jpeg"  properties="cover-image"/>
                %(manifest)s
                <item href="toc.xhtml" id="toc" type="application/xml+xhtml" properties="nav" />
                <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>
            </manifest>
            <spine toc="ncx">
                <itemref idref="titlepage"/>
                %(spine)s
                <itemref idref="toc"/>
            </spine>
            <guide>
                <reference type="toc" title="Table of Contents" href="toc.xhtml"/>
                <reference type="cover" title="Cover" href="titlepage.xhtml"/>
            </guide>
        </package>'''

    manifest = ""
    spine = ""
    metadata = '''<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">%(novelname)s</dc:title>
        <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:ns0="http://www.idpf.org/2007/opf" ns0:role="aut" ns0:file-as="Unbekannt">%(author)s</dc:creator>
        <dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>
        <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf" id="%(uuid)s" opf:scheme="uuid">%(uuid)s</dc:identifier>''' % {
        "novelname": novelname , "author": author, "uuid": uniqueid}

    # Write each HTML file to the ebook, collect information for the index
    for i, html in enumerate(html_files):
        basename = os.path.basename(html[0])
        manifest += '<item id="file_%s" href="%s" media-type="application/xhtml+xml"/>' % (
                      i+1, basename)
        spine += '<itemref idref="file_%s" />' % (i+1)
        epub.write(html[0], "OEBPS/"+basename)

    # Finally, write the index
    epub.writestr("OEBPS/Content.opf", index_tpl % {
        "metadata": metadata,
        "manifest": manifest ,
        "spine": spine,
        })

 #Generates a Table of Contents + lost strings
    toc_start = '''<?xml version='1.0' encoding='utf-8'?>
        <!DOCTYPE html>
        <html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
        <head>
            <title>%(novelname)s</title>
        </head>
        <body>
            <section class="frontmatter TableOfContents">
                <header>
                    <h1>Contents</h1>
                </header>
                <nav id="toc" role="doc-toc" epub:type="toc">
                    <ol>
                    %(toc_mid)s
            %(toc_end)s'''
    toc_mid = ""
    toc_end = '''</ol></nav></section></body></html>'''

    
    toc_ncx=""

    for i, y in enumerate(html_files):
        ident = 0
        chapter = y[1]
        chapter = str(chapter)
        toc_mid += '''<li class="toc-Chapter-rw" id="num_%s">
            <a href="%s">%s</a>
            </li>''' % (i, os.path.basename(y[0]), chapter)
        toc_ncx +=''' <navPoint class="chapter" id="nav%s" playOrder="%s">
      <navLabel>
        <text>%s</text>
      </navLabel>
      <content src="%s"/>
    </navPoint>''' %(i,i,chapter,os.path.basename(y[0]))

    toc_ncx_start='''<?xml version='1.0' encoding='utf-8'?>
    <ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1" xml:lang="en">

    <head>
    <meta name="dtb:uid" content="%(uuid)s"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle><text>%(title)s</text></docTitle>
    <navMap>%(navpoints)s</navMap>
    </ncx>'''% {"uuid" : uniqueid, "title":novelname,"navpoints" : toc_ncx}


    epub.writestr("OEBPS/toc.ncx", toc_ncx_start)
    epub.writestr("OEBPS/toc.xhtml", toc_start % {"novelname": novelname, "toc_mid": toc_mid, "toc_end": toc_end})
    epub.writestr("OEBPS/titlepage.xhtml",'''<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="calibre:cover" content="true" />
        <title>Cover</title>
        <style type="text/css" title="override_css">
            @page {padding: 0pt; margin:0pt}
            body { text-align: center; padding:0pt; margin: 0pt; }
        </style>
    </head>
    <body>
        <div>
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                width="100%" height="100%" viewBox="0 0 1000 1435"
                preserveAspectRatio="none">
                <image width="1000" height="1435" xlink:href="cover.jpg"/>
            </svg>
        </div>
    </body>
    </html>''')
    epub.write(coverfile, "OEBPS/cover.jpg")
    epub.close()


def getcover(src,novel):
    if  os.path.exists(os.path.join(novel,"cover.jpg")):
        return os.path.join(novel,"cover.jpg")
    ssl._create_default_https_context = ssl._create_unverified_context
    url = urllib.request.Request(
    	src,
    	data=None,
    	headers={
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
      	}
    )
    with urllib.request.urlopen(url) as response, open(os.path.join(novel,"cover.jpg"), 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
    return os.path.join(novel,"cover.jpg")
