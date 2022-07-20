import pandas as pd

df = pd.read_csv('musinsa_link_2022-07-20.csv', index_col=0)
df = df[:3]
print(df)
temp_list = [['dasdsadasd', 'dasdggsdfisadjdf', '12345667'], ['ㄴ야ㅏ론ㅁㅇ래네', 'ㄴㅇ매ㅣㅜㅊㅍㅁ냉ㄹ', 'ㅁ야ㅔㅐ누']]
df_1 = pd.DataFrame({'text': temp_list})
print(df_1)
df_left = pd.merge(df, df_1, left_index=True, right_index=True, how='left')
df_left.to_csv('test.csv')
print(df_left)