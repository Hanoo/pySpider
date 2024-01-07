import pymysql


class DBOperateSet(object):

    __conn = None

    def __init__(self):
        self.__conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='mysql',
            db='chengyuwan',
            charset='utf8')

    def before_quit(self):
        self.__conn.close()

    def insert(self, chengyu_info):
        cursor = self.__conn.cursor()
        sql = 'INSERT INTO chengyu (idiom, detail_url, simple_description, letter_index, explain) VALUES (%s,%s,%s,%s,%s)'
        rows = cursor.execute(sql, (chengyu_info.detail_url, chengyu_info.simple_description,
                                    chengyu_info.letter_index, chengyu_info.explain))
        self.__conn.commit()
        cursor.close()
        print(rows)

    def insert_batch(self, data_in_list):
        cursor = self.__conn.cursor()
        sql = 'INSERT INTO chengyu (idiom, detail_url, simple_description, letter_index, explanation) VALUES (%s,%s,%s,%s,%s)'
        rows = cursor.executemany(sql, data_in_list)
        self.__conn.commit()
        cursor.close()
        print(rows)


if __name__ == "__main__":
    db_oper = DBOperateSet()
    test_data = [
        ('http://www.baidu.com', 'simple_description111111', 'b', 'asdfasdfasdfasdfasd'),
        ('http://www.pcg.biz', 'simple_description2222', 'p', 'Iadfasdfasdfasdfasdfasd')
    ]
    db_oper.insert_batch(test_data)
