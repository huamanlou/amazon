# -*- coding: utf-8 -*-
import MySQLdb
import time
import ConfigParser
#mysql数据库方法
class MysqlDo:
    host = ''
    user = ''
    passwd = ''
    db = ''
    charset = ''
    conn = ''
    def __init__(self):
        conf = ConfigParser.ConfigParser()
        conf.read('database.conf')
        self.host = conf.get('mysql_db', 'host')
        self.user = conf.get('mysql_db', 'user')
        self.passwd = conf.get('mysql_db', 'passwd')
        self.db = conf.get('mysql_db', 'db')
        self.charset = conf.get('mysql_db', 'charset')

        self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db, charset=self.charset)

    def close_conn(self):
        self.conn.close()
    #查找索引表
    def select_asin(self, asin):
        cursor = self.conn.cursor()
        cursor.execute("select * from t_asin where asin= '%s'" % (asin))
        row = cursor.fetchall()
        # self.conn.close()
        return len(row)
    #插入索引表
    def insert_asin(self, asin):
        cursor = self.conn.cursor()
        ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        sql = "insert into t_asin(asin,ctime,status) value ('%s', '%s', '%d')"
        cursor.execute(sql % (asin,ctime,1))
        self.conn.commit()

    #标志索引表商品是亚马逊自营书籍
    def update_asin_isbook(self, asin):
        cursor = self.conn.cursor()
        # 更新状态
        sql = "update t_asin set isbook = 1 where asin = '%s'" % (asin)
        # 执行SQL语句
        cursor.execute(sql)
        self.conn.commit()

    #查找爬虫任务表
    def select_scrapy(self, num):
        cursor = self.conn.cursor()
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        #暂时不限制时间
        #cursor.execute("select asin from t_scrapy where status=0 and date='%s' limit %d" % (date,num))
        cursor.execute("select asin from t_scrapy where status=0 limit %d" % (num))
        asin_rows = cursor.fetchall()
        #这里有个坑，取出来是双层tuple,但是mysql可以执行，下面无法直接取值
        if len(asin_rows) == 0:
            return 0

        #todo -- 更新状态,拼接in 语句没成功，先循环处理,
        # asin_list = ','.join(['%s'] * len(row))
        # sql = "update t_scrapy set status = 1 where asin in (%s)" % (asin_list)
        # # 执行SQL语句
        # cursor.execute(sql, row)
        # # 提交到数据库执行
        # self.conn.commit()

        for asin in asin_rows:
            #sql = "update t_scrapy set status = 1 where asin = '%s' and date='%s'" % (asin[0],date)
            sql = "update t_scrapy set status = 1 where asin = '%s'" % (asin[0])
            # 执行SQL语句
            cursor.execute(sql)
            # 提交到数据库执行
            self.conn.commit()

        return asin_rows
    #查询爬虫队列现在还有多少
    def count_scrapy(self):
        cursor = self.conn.cursor()
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        # query = "select * from t_scrapy where status=1 and date='%s'" % (date)
        query = "select * from t_scrapy where status=1"
        cursor.execute(query)
        row_num = cursor.rowcount
        return row_num

    #更新爬虫任务标志位
    def update_scrapy(self, asin):
        cursor = self.conn.cursor()
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        #更新状态
        sql = "update t_scrapy set status = 2 where asin = '%s'" % (asin)
        # 执行SQL语句
        cursor.execute(sql)
        # 提交到数据库执行
        self.conn.commit()
