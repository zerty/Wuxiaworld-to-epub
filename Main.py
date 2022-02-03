
from __future__ import print_function

import logging
import os
import os.path
import sonora.client
import html
from time import sleep
import random

import chapter2_pb2
import chapter2_pb2_grpc
import novel_pb2
import novel_pb2_grpc


from google.protobuf import wrappers_pb2 


from epub import *


def get_chapter_content(stub,novel,chapter):
    chapterreq=chapter2_pb2.GetChapterRequest(chapterProperty=chapter2_pb2.GetChapterByProperty(slugs=chapter2_pb2.ByNovelAndChapterSlug(novelSlug=novel ,chapterSlug=chapter)))
    feature = stub.GetChapter(chapterreq)
    return str(feature.item.content.value)

def get_novel_info(stub,name):
    novelreq=novel_pb2.GetNovelRequest(slug=name)
    feature=stub.GetNovel(novelreq)
    return feature

def get_chapter_list(stub,id):
    clistreq=chapter2_pb2.GetChapterListRequest(novelId = id)
    feature=stub.GetChapterList(clistreq)
    return feature

def run(_name,bybook=False):
    #create folder if necessary
    if not os.path.exists(_name):
        os.makedirs(_name)


    #use sonora client
    with sonora.client.insecure_web_channel(f"http://api.wuxiaworld.com") as channel:
    
        # create stub for grpc access
        chapstub = chapter2_pb2_grpc.ChaptersStub(channel)
        novelstub= novel_pb2_grpc.NovelsStub(channel)

        # get novel information
        novelinfo=get_novel_info(novelstub,_name)

        #get chapter list
        chapterlist=get_chapter_list(chapstub,novelinfo.item.id)

        #get cover
        cover=getcover(novelinfo.item.coverUrl.value,_name)

        #get author
        author=novelinfo.item.authorName.value

        print("== {} by {} ==".format(novelinfo.item.name,author))

        #dowloading all chapters if necessary to a list [title, chapter content] and generate html for chapter
        #and generate one epub per book/part
        #print("Found {} Books".format(str(len(chapterlist.items))))
        fullhtml=[]
        nbnewchap=0
        for i in range(0,len(chapterlist.items)):
            htmls=[]
            update=False
            bookname=novelinfo.item.name+'-'+chapterlist.items[i].title.replace(":","")
            
            #print(" * Book {}".format(bookname))
            #print("  - Found {} Chapters".format(str(len(chapterlist.items[i].chapterList))))
            for j in range(0,len(chapterlist.items[i].chapterList)):
                filename = os.path.join(_name,"chapter_"+str(f'{i:04}')+"-"+str(f'{j:04}')+".xhtml")
                if not os.path.exists(filename):
                    sleep(0.1+(random.random()*0.1))
                    nbnewchap+=1
                    update=True
                    content=html.unescape(get_chapter_content(chapstub,novelinfo.item.slug,chapterlist.items[i].chapterList[j].slug)).replace(u'\xa0', u' ')
                    makechapter(chapterlist.items[i].chapterList[j].name,content,filename)
                htmls.append([filename,chapterlist.items[i].chapterList[j].name])
                fullhtml.append([filename,chapterlist.items[i].chapterList[j].name])
            
            if(bybook and (update or not os.path.exists(os.path.join("output",bookname)  + ".epub"))):
                print("  - Creating Updating Ebook {}".format(bookname))
                generate_epub(htmls,bookname ,author,cover)

        print("  Total New chapters : {}".format(nbnewchap))
        if ((nbnewchap>0 or  not os.path.exists(os.path.join("output",_name)  + ".epub")) and not (bybook)):
            print("  - Creating Updating Full Ebook")
            generate_epub(fullhtml,_name ,author,cover)

if __name__ == '__main__':
    logging.basicConfig()
    # use the last element of the novel url to grab it ex: https://www.wuxiaworld.com/novel/absolute-resonance would be absolute-resonance
    run("against-the-gods",bybook=True)