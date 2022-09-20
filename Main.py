
from __future__ import print_function

import logging
import os
import os.path
#import sonora.client
import html
from time import sleep
import random

import wuxiaworld_v2_pb2
import wuxiaworld_v2_pb2_grpc

from seleniumwire.undetected_chromedriver.v2 import Chrome, ChromeOptions

from google.protobuf import wrappers_pb2 


from epub import *
from scrpcweb import *



def get_chapter_content(stub,novel,chapter):
    chapterreq=wuxiaworld_v2_pb2.GetChapterRequest(chapterProperty=wuxiaworld_v2_pb2.GetChapterByProperty(slugs=wuxiaworld_v2_pb2.ByNovelAndChapterSlug(novelSlug=novel ,chapterSlug=chapter)))
    feature = stub.GetChapter(chapterreq) 
    #print(feature.item.content.value)
    #return str(feature.item.content.value)
    return feature

def get_novel_info(stub,name):
    novelreq=wuxiaworld_v2_pb2.GetNovelRequest(slug=name)
    feature=stub.GetNovel(novelreq)
    return feature

def get_chapter_list(stub,id):
    clistreq=wuxiaworld_v2_pb2.GetChapterListRequest(novelId = id)
    feature=stub.GetChapterList(clistreq)
    #print(feature)
    return feature

def run(_name,bybook=False):
    #create folder if necessary
    if not os.path.exists(_name):
        os.makedirs(_name)


    #use sonora client
    # channel._metadata = [
    #     ("Origin","https://www.wuxiaworld.com"),
    #     ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0"),
    #     ("content-type", "application/grpc-web+proto"),
    #     ("authorization",""),
    #     ("x-grpc-web", "1")
    # ]

    # create stub for grpc access
    chapstub = wuxiaworld_v2_pb2_grpc.ChaptersStub(channel)
    novelstub= wuxiaworld_v2_pb2_grpc.NovelsStub(channel)

    # get novel information
    novelinfo=get_novel_info(novelstub,_name)

    #get chapter list
    
    chapterlist=get_chapter_list(chapstub,novelinfo.item.id)

    #get cover
    cover=getcover(novelinfo.item.coverUrl.value,_name)

    #get author
    author=novelinfo.item.authorName.value
    print("")
    print("== {} by {} ==".format(novelinfo.item.name,author))

    #dowloading all chapters if necessary to a list [title, chapter content] and generate html for chapter
    #and generate one epub per book/part
    
    fullhtml=[]
    nbnewchap=0
    for i in range(0,len(chapterlist.items)):
        htmls=[]
        update=False
        bookname=novelinfo.item.name+'-'+chapterlist.items[i].title.replace(":","")
        for j in range(0,len(chapterlist.items[i].chapterList)):
            filename = os.path.join(_name,"chapter_"+str(f'{i:04}')+"-"+str(f'{j:04}')+".xhtml")
            if (not os.path.exists(filename) or os.path.getsize(filename)<4*1024):
                sleep(0.5+random.random()*2)
                if (os.path.exists(filename)) : os.remove(filename) 
                chapter=get_chapter_content(chapstub,novelinfo.item.slug,chapterlist.items[i].chapterList[j].slug)
                if (len(chapter.item.content.value) >0):
                    content=html.unescape(str(chapter.item.content.value)).replace(u'\xa0', u' ')
                    makechapter(chapterlist.items[i].chapterList[j].name,content,filename)
                    nbnewchap+=1
                    htmls.append([filename,chapterlist.items[i].chapterList[j].name])
                    fullhtml.append([filename,chapterlist.items[i].chapterList[j].name])
                    update=True

            else:        
                htmls.append([filename,chapterlist.items[i].chapterList[j].name])
                fullhtml.append([filename,chapterlist.items[i].chapterList[j].name])
        
        if(bybook and (update or not os.path.exists(os.path.join("output",bookname)  + ".epub"))):
            print("  - Creating or Updating Ebook {}".format(bookname))
            generate_epub(htmls,bookname ,author,cover)

    print(" Total chapters: {},  Total New chapters : {}".format(str(len(fullhtml)),nbnewchap))
    if ((nbnewchap>0 or  not os.path.exists(os.path.join("output",_name)  + ".epub")) and not (bybook)):
        print("  - Creating or Updating Full Ebook")
        generate_epub(fullhtml,_name ,author,cover)

if __name__ == '__main__':
    logging.basicConfig()


    #channel=sonora.client.insecure_web_channel(f"https://api2.wuxiaworld.com")
    #sleep(7)
    channel=insecure_web_channel(f"https://api2.wuxiaworld.com")
    



    run("keyboard-immortal",bybook=True)
    # run("emperors-domination",bybook=False)
    # run("nine-star-hegemon",bybook=True)
    # run("overgeared",bybook=False)
    # run("star-odyssey",bybook=True)
    # run("necropolis-immortal",bybook=True)
