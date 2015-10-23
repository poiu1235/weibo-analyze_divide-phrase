#!/usr/bin/env python
#_*_ coding: utf-8_*_
'''
Created on 2015-10-19

@author: luis
'''
from luis.ConnSQL import ConnSQL


if __name__ == '__main__':
    connSQL=ConnSQL()
    cc=connSQL.insertdivcont("content")
    tt=connSQL.insertdivcont("tag")
    rr=connSQL.insertdivcont("remark")