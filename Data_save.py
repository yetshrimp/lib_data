from sqlalchemy import create_engine
import pandas as pd


important_data = pd.read_excel('logIn.xlsx')


class DataSaver(object):
    def __init__(self):
        self.host = important_data['sqlhost'].iloc[0]
        self.password = important_data['sqlpsw'].iloc[0]
        self.db_name = important_data['dbname'].iloc[0]
        self.table_name = important_data['table_name'].iloc[0]

    def save(self, df):
        engine = create_engine(
            'mysql+pymysql://root:%s@%s/%s' % (self.password, self.host, self.db_name), encoding='utf-8'
        )
        try:
            df.to_sql(self.table_name, con=engine, if_exists='append', index=False)
        except:
            print('储存失败')


# if __name__ == '__main__':
#     df = pd.DataFrame({'id': ['2', '3'], 'username': ['112', '223']})
#     data_saver = DataSaver()
#     data_saver.save(df)
