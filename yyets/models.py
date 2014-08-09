import pymysql

class MySQLDB(object):

    def __init__(self):
        pass

    def get_cursor(self):
        conn = pymysql.connect(user='', passwd='', db='', host='',  charset="utf8", use_unicode=True)
        return conn.cursor()

class ShowsDB(MySQLDB):

    def get_updated_time_by_show_id(self, show_id_list):

        cursor = self.get_cursor()

        sql = '''SELECT show_id, updated_time FROM shows WHERE show_id IN (%s)'''
        in_p = ', '.join(list(map(lambda x: '%s', show_id_list)))
        sql = sql % in_p

        show_id_set = tuple(show_id_list)
        cursor.execute(sql, show_id_set)
        updated_times = cursor.fetchall()

        u_dict = {}
        for u in updated_times:
            u_dict[u[0]] = u[1]
        print u_dict
        return u_dict



if __name__ == '__main__':

    S = ShowsDB()

    print S.get_updated_time_by_show_id(['10453', '10588', '10796'])

