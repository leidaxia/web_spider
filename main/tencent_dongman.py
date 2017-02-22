#coding=utf-8
import re
import urllib2
import urllib
from bs4 import BeautifulSoup
import lxml.html as HTML
import MySQLdb
import os
import threading,time

def getHtml(url):
    html=''
    print " It is parsing webpage:%s" %url
    try:
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        html = response.read()
    except:
        html='null'
    return html

#获取vid 开始下载程序
def get_title_vid(url): #获取downloadurl 开始下载电视剧
  
    html=getHtml(url)
    if html:
        #<h1 class="mod_player_title"><strong title="变形金刚之能量晶体" id="h1_title" >变形金刚之能量晶体</strong></h1>
        rexp=r'<h1 class="mod_player_title"><strong title="(.+?)" id="(.+?)" >(.+?)</strong></h1>'
        try:
            filename_m = re.findall( rexp , html)
            if filename_m:
                print filename_m[0][0]
                filename=filename_m[0][0]
                filename=filename.decode('utf-8').encode('gbk')
                    
            path='e:\\dongman\\'
            new_path = os.path.join(path, filename)
            if not os.path.isdir(new_path):
                os.makedirs(new_path)
            newpath='e:\\dongman\\'+filename+'\\'
        except:
            print 'ERROR'
            
            
        dom = HTML.document_fromstring(html)
        trNodesList=dom.xpath("//a[@target='_self']")
        if trNodesList:
            for node in  trNodesList: 
                try:
                    vid=node.get('id')
                    title=node.get('title')
                    downloadurl=get_downloadurl(vid)
                    if downloadurl:
                        downloadFilm(downloadurl,newpath,title)
                except:
                    print 'not found this film'
                

#获取真正下载地址
def get_downloadurl(vid):
    downloadxmlurl='http://vv.video.qq.com/geturl?otype=xml&platform=1&vid=%s&format=2' % vid
    html=getHtml(downloadxmlurl)
    if html:
        rexp=r'<url>(.+?)</url>'
        link_m = re.findall( rexp , html)
        if link_m[0]:
            downloadurl=link_m[0]
    return downloadurl

#下载电影程序
def downloadFilm(downloadurl,filepath,title):
    #title=title.decode('utf-8').encode('gbk')
    title=title.encode('gbk')
    path=filepath+title+'.mp4'
    wget_cmdline ='wget robots=off -O %s %s' %(path,downloadurl)
    os.system(wget_cmdline)

#获取所有电影链接    
def getFirstLinks(url):
    Links=[]
    html=getHtml(url)
    if html:
        #<A title=贝瓦儿歌 href="http://v.qq.com/cover/e/e51zela13gm1zno.html" target=_blank>贝瓦儿歌</A>
        #<h6 class="scores"><a href="http://v.qq.com/cover/j/j324wyy9rpo9dqn.html" title="海底小纵队经典特辑" target="_blank">海底小纵队经典特辑</a>
        #rexp=r'<a href="(.+?)" title="(.+?)" target=_blank>(.+?)</a>'
        rexp=r'<h6 class="scores"><a href="(.+?)" title="(.+?)" target="_blank">(.+?)</a>'
        link_m = re.findall( rexp , html)
        if link_m:
            for m in link_m:
                print m[0]
                Links.append(m[0])
        else:
            print 'NOT FOUND'
        return Links
    else:
        return 'null' 
     
def insertleiDb(title,type,area,years,summary): 
    '''
    conn= MySQLdb.connect(
         host='127.0.0.1',
        port = 3306,
        user='root',
        passwd='root',
        db ='police_news',
        
        )
    '''
    conn=MySQLdb.connect('localhost','root','root','lei_dongman',charset='utf8')
    cur = conn.cursor()
    #cur.execute("insert into news_table values(source,url,title,content,writer,time)")
    cur.execute("INSERT INTO dongman_table(title,type,area,years,summary) VALUES(%s,%s,%s,%s,%s)",(title,type,area,years,summary))
    print 'INSERTED SUCCESSFULLY'
    cur.close()
    conn.commit()
    conn.close()
    
#获取电影简介、地区、类型等   
def getInfo(url):
    html=getHtml(url)
    if html:
        #<h1 class="mod_player_title"><strong title="变形金刚之能量晶体" id="h1_title" >变形金刚之能量晶体</strong></h1>
        rexp=r'<h1 class="mod_player_title"><strong title="(.+?)" id="(.+?)" >(.+?)</strong></h1>'
        try:
            filename_m = re.findall( rexp , html)
            if filename_m:
                print filename_m[0][0]
                filename=filename_m[0][0]
                #filename=filename.decode('utf-8').encode('gbk')
                title=filename
        except:
            title='null'
        '''   
        dom = HTML.document_fromstring(html)
        trNodesList=dom.xpath("//div[@cLass='info_category']")
        #if trNodesList:
        print trNodesList
        '''
        soup = BeautifulSoup(html)    
        divs = soup.find_all('div', {'class' : 'info_category'})
        #print divs[0]
        if divs:
            type=''
            re_info=r'<a (.+?)>(.+?)</a>' 
            p_info = re.compile(re_info, re.DOTALL)
            m_info = p_info.findall(str(divs[0]))
            #print m_info
            if m_info:
                #k=len(m_info)
                s=''
                for m in m_info:
                    s+=m[1]+' '
                type=s
                print '类型:%s' %type
            else:
                type='null'
        else:
            type='null'
                
        soup = BeautifulSoup(html)    
        divs = soup.find_all('div', {'class' : 'info_area'})
        #print divs[0]
        if divs:
            area=''
            re_info=r'<a (.+?)>(.+?)</a>' 
            p_info = re.compile(re_info, re.DOTALL)
            m_info = p_info.findall(str(divs[0]))
            #print m_info
            if m_info:
                #k=len(m_info)
                s=''
                for m in m_info:
                    s+=m[1]+' '
                area=s
                print '地区:%s' %area
            else:
                area='null'
        
        soup = BeautifulSoup(html)    
        divs = soup.find_all('div', {'class' : 'info_years'})
        #print divs[0]
        if divs:
            yeas=''
            re_info=r'<a (.+?)>(.+?)</a>' 
            p_info = re.compile(re_info, re.DOTALL)
            m_info = p_info.findall(str(divs[0]))
            #print m_info
            if m_info:
                #k=len(m_info)
                s=''
                for m in m_info:
                    s+=m[1]+' '
                years=s
                print '年份:%s' %years
        else:
            years='null'
                
        dom = HTML.document_fromstring(html)
        trNodesList=dom.xpath("//div[@id='mod_desc']//span[@class='desc']")
        if trNodesList:
            #print trNodesList
            summary=trNodesList[0].text_content()
            summary = ' '.join(summary.split()) 
            print summary
        else:
            summary='null'
        try:
            insertleiDb(title,type,area,years,summary)
        except:
            pass
     

class Start_DownThread(threading.Thread):
    ''' 开始下载具体网页url '''
    def __init__(self,url):
        threading.Thread.__init__(self)
        self.url = url
    def run(self):
        get_title_vid(self.url) #开始下载电影
        getInfo(self.url)       #获取电影内容

if __name__ == '__main__':
    baseUrls=[]
    aliveThreadDict = {}        # alive thread
    downloadingUrlDict = {}     # downloading link
    '''
    for i in range(0,50): 
        url='http://zhannei.baidu.com/cse/search?q=%E5%90%88%E8%82%A5%E8%AD%A6%E5%AF%9F&p='+str(i)+'&s=18320806464747503807'
        baseUrls.append(url)
    '''
    for i in range(0,5):
        j=i%10
        url='http://v.qq.com/cartlist/'+str(j)+'/3_-1_-1_-1_-1_1_'+str(i)+'_0_20.html'
        links=getFirstLinks(url)
        baseUrls.extend(links)
        for link in links:
            print link
    i = 0;
    while i < len(baseUrls):
        # Note:我听评说网 只允许同时有三个线程下载同一部小说，但是有时受网络等影响，\
        #     为确保下载的是真实的mp3，这里将线程数设为2 
        while len(downloadingUrlDict)< 5 :
            downloadingUrlDict[i]=i
            i += 1
        for urlIndex in downloadingUrlDict.values():
            if urlIndex not in aliveThreadDict.values():  #判断线程是否已经启动过了
                
                t = Start_DownThread(baseUrls[urlIndex])  #t为线程类的对象
                t.start()
                aliveThreadDict[t]=urlIndex
        for (th,urlIndex) in aliveThreadDict.items():
            if th.isAlive() is not True:
                del aliveThreadDict[th] # delete the thread slot
                del downloadingUrlDict[urlIndex] # delete the url from url list needed to download 
    
    print '-------------------------下载完成--------------------------------------'
    
  
        
        
        
