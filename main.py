from utils import *

text = open(r"C:\Users\User\PycharmProjects\Твої вершини\Українські вершини.txt", 'r', encoding='UTF-8')
data = convert_data(text)

df = pd.DataFrame(data)
df = df.sort_values(by=['Height'], ascending=False)

print(df.to_string())




