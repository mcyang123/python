# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 13:40:06 2015
爬取     求职位的数据
确定要获取数据的条件---->获取数据------>整理数据------->将数据存入数据库
数据模型：
职位名称
公司名称
工作地点
工资
学历要求
工作年限
技术要求
年龄
发布时间

@author: MIKE
"""
import urllib2
import urllib
import re
import os
import sys
#import xlwt
reload(sys)
sys.setdefaultencoding('gbk')


class spider_job(object):
    def __init__(self):
        self.data = {'jobid':'',
                     'jobname':'',                  #职位名称
                     'loc':'',                      #工作地点
                     'company':'',                  #公司名称
                     'pay':'',                      #工资
                     'degree':'',                   #学历
                     'limityears':'',               #工作年限
                     #'age':'',                      #要求年龄
                     'tec':'' ,                     #技术要求
                     'url':''                       #链接
                       } 
        self.keyword = raw_input('input keyword:')  #搜索关键字
        self.keyword = urllib.quote(self.keyword.encode('utf8'))
        #sys.setdefaultencoding('utf8')
        self.c_page = 0                          #当前页
        self.id = 1
        #当前URL
        self.host = 'http://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E9%80%89%E6%8B%A9%E5%9C%B0%E5%8C%BA'
        self.Datatype = 1      
        self.c_url = ''            
        self.url_list=[]                           #url队列
        self.path = 'E:\\project_file\\python\\spider_job\\zhilian\\'
        #self.book = xlwt.Workbook(encoding='utf8',style_compression=0)
        #self.sheet = self.book.add_sheet('sheet1',cell_overwrite_ok = True)
        #self.line = 1
        
    def get_page(self) :
        """
        获取URL的代码，若出现错误则将现有数据保存到文件中
        html: 获取的网站代码
        url：要获取的URL
        f：保存数据的文件对象
        """
        html = ''    
        self.Datatype = 1                   #初始化，默认网页是第二层
        if len(self.url_list) == 0:         #队列为空，表明应该指向下一页
            c_url = self.host+'&'+'kw='+self.keyword+'&p='+str(self.c_page)
            #c_url = urllib.quote(c_url.decode('gbk','replace').encode('utf8','replace'))
            #self.book.save('zhilian.xls')
            f = open(self.path+'url_list.txt','a')
            f.write('page:'+str(self.c_page)+'\n')
            f.close()
            self.c_page +=1
            self.id = 1
            self.url_list += [c_url]
            self.Datatype =0                #换页后，网页类型为第一层
        self.c_url = self.url_list[0]
        url = self.c_url
        print url
        try :
            html = urllib2.urlopen(url,timeout=10).read()#.decode("utf-8")
        except urllib2.URLError, e :
            if hasattr(e, "code"):
                print "The server couldn't fulfill the request."
                print "Error code: %s" % e.code
            elif hasattr(e, "reason"):
                print "We failed to reach a server. Please check your url and read the Reason"
                print "Reason: %s" % e.reason
            self.get_err_URL('url error ;id='+self.data['jobid'])
        except :
            print 'url error'
            self.get_err_URL('timeout;id='+self.data['jobid'])
        self.url_list.remove(self.c_url)
        return html
        
    def process(self,page):
        if page!='':
            if self.Datatype == 0 :                                   #第一层网页的处理
                temp = re.findall('id="newlist_list_content_table"(.+?)class="newlist_list_top clearfix"',page,re.S)
                if len(temp)>0 : 
                    self.get_url(temp[0])
                else:
                    print 'get job list error'
            if self.Datatype ==1:                                      #第二层网页处理
                self.data['jobid'] = str(self.c_page)+'-'+str(self.id)
                jobname = re.findall('class="inner-left fl.+?<h1>(.+?)</h1>',page,re.S)
                company= re.findall('class="inner-left fl.+?<h2>.+?>(.+?)<',page,re.S)
                tec = re.findall('<!-- SWSStringCutStart -->.+?>(.+?)<!-- SWSStringCutEnd -->',page,re.S)
                loc = re.findall('class="terminalpage-left".+?<a.+?>(.+?)<',page,re.S)
                info = re.findall('class="terminalpage-left".+?<ul(.+?)</ul>',page,re.S)
                if len(info)==0 :info = [''];self.get_err_URL('info error ;id='+self.data['jobid'])
                info =re.findall('<strong>(.+?)</strong>',info[0],re.S)
                if len(info) <8: info = ['']*8; self.get_err_URL('degree\years\age\pay error;id='+self.data['jobid'])
                degree = info[5]
                pay = info[0]
                limityears = info[4]
                
                if len(jobname) == 0: jobname = ['']; self.get_err_URL('jobname error ;id='+self.data['jobid'])
                if len(company) == 0:company = ['']; self.get_err_URL('company error ;id='+self.data['jobid'])
                if len(loc) == 0:loc = ['']; self.get_err_URL('loc error ;id='+self.data['jobid'])
                if len(tec) == 0:tec = ['']; self.get_err_URL('tec error ;id='+self.data['jobid'])
                
                self.data['jobname'] = jobname[0].strip()
                self.data['pay'] = pay.strip()
                self.data['company'] = company[0].strip()
                self.data['loc'] = loc[0].strip()           
                self.data['degree'] = degree.strip()
                self.data['limityears'] = limityears.strip()
                self.data['tec'] = tec[0].strip()
                self.data['url'] = self.c_url
                filename = self.data['jobid']+'.txt'
                self.store_data(filename)
                self.id +=1
                
        else:
            print "get data error!"
    
    def get_url(self,subpage):
        href = re.findall('<table.+?<div.+?href="(.+?)"',subpage,re.S)
        if len(href) == 0:  #获取不到URL
            print 'get href error'
        else:   #将URL加入队列
            self.url_list += href
            f = open(self.path+'\\url_list.txt','a')
            for u in href:
                f.write(u+'\n')
            f.close()
                
    def store_data(self,filename):
        s = ''
        for key, value in self.data.iteritems():
            s += key+':'+value+'\n'
        f = open(self.path+ filename,'w')
        f.write(s)
        f.close()
            
    def get_err_URL(self,info):
        f = open(self.path+'\\error_url.txt','a')
        f.write(self.c_url+'  error info:'+info+'\n')
        f.close()
        
if __name__ == '__main__':
    job = spider_job()
    print 'spider star.....'
    while job.c_page<0  :   #page<102
        page = job.get_page()
        job.process(page)
    #job.book.save('zhilian.xls')
    
        