import random
import linecache

def random_lines(filename):
    #rangeの中の数字はセリフデータの行数です。適宜変更してください。
    idxs = random.sample(range(500), 200)
    return [linecache.getline(filename, i) for i in idxs]

def DataPrep(file1,file2):
    text = random_lines(file1)
    f = open(file2,"w",encoding="utf-8")
    f.writelines(text)
    f.close()
