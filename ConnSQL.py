#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-10-19

@author: luis
'''


import ConfigParser
import MySQLdb
import jieba.analyse
jieba.load_userdict('bigdic.txt')
import os
import pymongo
import time


#import jieba
class ConnSQL(object):
    '''
    classdocs
    '''
    def __init__(self):
        self.client=None
        pass
    def initionMo(self):
        config=self.getconfig()
        self.client = pymongo.MongoClient(config[2], 27017);
        self.db = self.client.weibocatch
    def list_to_dict(self,obj,name):
        strx='{"'+name+'":['
        for i in obj:
            strx=strx+'"'+i+'",'
        if(len(obj)!=0):
            strx=strx[:-1]
        strx=strx+']}'
        return strx 
    def class_to_dict(self,obj):
        '''把对象(支持单个对象、list、set)转换成字典'''
        is_list = obj.__class__ == [].__class__
        is_set = obj.__class__ == set().__class__
        if is_list or is_set:
            obj_arr = []
            for o in obj:
                #把Object对象转换成Dict对象
                dic = {}
                dic.update(o.__dict__)
                obj_arr.append(dic)
            return obj_arr
        else:
            dic = {}
            dic.update(obj.__dict__)
            return dic
    def getconfig(self):
        try:
            config=ConfigParser.ConfigParser()
            with open('localconfig','r') as cfgfile:
                config.readfp(cfgfile)
                DBUSERNAME=config.get('db','dbuser')
                DBPASSWD=config.get('db','dbpwd')
                DBSITE=config.get('db','dbsite')
                return (DBUSERNAME,DBPASSWD,DBSITE)
        except:
            print "no config"
            os._exit()
           
    def inition(self):
        config=self.getconfig()
        self.conn=MySQLdb.Connect(host=config[2],user=config[0],passwd=config[1])#,charset='utf8'
        #选择数据库     
        self.conn.select_db('weibocatch');
    def insertdivcont(self,casetag):
        ftag=True
        count=0
        while(ftag):
            try:
                self.inition()
                #获取操作游标     
                cursor = self.conn.cursor()
                #注意一下啊，flag=0 未扒取任何内容，flag=1 扒取了用户关系，flag=2 扒取了微博信息
                #爬取用户信息用flag=0
                #爬取微博信息用flag=1
                if(casetag=="content"):
                    cursor.execute("""(select weiboid,wid,'**********' as transferid,content from w_content where flag=0 limit 1) 
                                    union 
                                    (select weiboid,wid,transferid,content from w_transfer where flag=0 limit 1);""")
                elif(casetag=="tag"):
                    cursor.execute("""(select weiboid,wid,'**********' as transferid,label from w_content where flag=1 and label!='' limit 1) 
                                    union 
                                    (select weiboid,wid,transferid,label from w_transfer where flag=1 and label!='' limit 1);""")
                elif(casetag=="remark"):
                    cursor.execute("""(select weiboid,wid,transferid,remark from w_transfer where flag=2 and remark!='' limit 1);""")

                #"只获取一条记录:"   
                result = cursor.fetchone();#这个返回的是一个tuple
                if(result!=None):
                    strweiboid=result[0]
                    strwid=result[1]
                    strtransid=result[2]
                    seg_list=jieba.cut(result[3].replace('\'','')
                                       .replace('"','').replace('【','')
                                       .replace('】','').replace('\\','')
                                       .replace('/',''),cut_all=False)#分词,这里返回的是generator类型，这个类型有个特别坑的地方
                    #每用一次，偏移量后移一个，用完一次内容就全部没了。。。
                    listseg=list(seg_list)
                    str_res=("/").join(listseg)
                    tags = jieba.analyse.extract_tags(result[3].replace('\'','')
                                       .replace('"','').replace('【','')
                                       .replace('】','').replace('\\','')
                                       .replace('/',''),20)#提取关键字
                    listtag=list(tags)
                    str_tag=(",").join(listtag)
                    if(casetag=="content"):
                        cursor.execute("""INSERT INTO weibocatch.div_content
                                        (weiboid,wid,wtransid,cpart,ccore)
                                        VALUES (%s,%s,%s,%s,%s);
                                        """,(strweiboid,strwid,strtransid,str_res.encode('utf8'),str_tag.encode('utf8')))
                        ii=cursor.execute("""update w_content set flag=1 where weiboid=%s;""",(strweiboid))
                        if(ii==0):
                            cursor.execute("""update w_transfer set flag=1 where weiboid=%s;""",(strweiboid))
                    elif(casetag=="tag"):#不同的部分 sql 语句里的字段名都变了
                        cursor.execute("""INSERT INTO weibocatch.div_tag
                                        (weiboid,wid,wtransid,tpart,tcore)
                                        VALUES (%s,%s,%s,%s,%s);
                                        """,(strweiboid,strwid,strtransid,str_res.encode('utf8'),str_tag.encode('utf8')))
                        ii=cursor.execute("""update w_content set flag=2 where weiboid=%s;""",(strweiboid))
                        if(ii==0):
                            cursor.execute("""update w_transfer set flag=2 where weiboid=%s;""",(strweiboid))
                    elif(casetag=="remark"):#不同的部分 sql 语句里的字段名都变了
                        cursor.execute("""INSERT INTO weibocatch.div_remark
                                        (weiboid,wid,wtransid,rpart,rcore)
                                        VALUES (%s,%s,%s,%s,%s);
                                        """,(strweiboid,strwid,strtransid,str_res.encode('utf8'),str_tag.encode('utf8')))
                        #remark 只有 转发才有
                        cursor.execute("""update w_transfer set flag=3 where weiboid=%s;""",(strweiboid))
                    self.conn.commit()           
                    contentdiv=self.list_to_dict(listseg,"listseg")
                    corediv=self.list_to_dict(listtag, "listtag")
                    #这里的反斜杠是换行写的意思
                    divall="{\"weiboid\":\""+strweiboid+"\","\
                            +"\"wid\":\""+strwid+"\","\
                            +"\"wtransid\":\""+strtransid+"\","\
                            +contentdiv[1:-1]+","+corediv[1:-1]+"}"
                    print divall
                    self.initionMo()
                    table1=None
                    if(casetag=="content"):
                        table1=self.db.divcontent
                    elif(casetag=="tag"):
                        table1=self.db.divtag
                    elif(casetag=="remark"):
                        table1=self.db.divremark
                    table1.insert_one(eval(divall))#eval()用来把串串转成json
                    count=count+1
                    print time.strftime('%H-%M-%S')+": "+casetag+" : "+"已经处理了" +str(count)
                    if(count%1000==0):
                        time.sleep(10)
                else:
                    ftag=False
            except Exception as err:
                self.conn.rollback()
                print time.strftime('%H-%M-%S')+":"+str(err)
            finally:
                #关闭连接，释放资源     
                cursor.close(); 
                self.conn.close()
                if(self.client!=None):
                    self.client.close()   
if __name__ == '__main__':
    connSQL=ConnSQL()
    hh=connSQL.insertdivcont()
