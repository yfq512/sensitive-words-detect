import requests
from urllib import parse
import json
# from keywords_fit import nsword_fit as nsw_fit
import base64
import os, time, shutil, fcntl, random
import jieba

def clean_str(text_list):
    pass_sign = [' ','`','~','!','@','#','$','%','^','&','*','(',')','-','_','+','=','{','}','[',']','|',':',';','"','?','/','<','>',',','.','：','；','“','‘','《','》','，','。','？']
    x = []
    for n in text_list:
        if not n in pass_sign:
            x.append(n)
    # 对相邻词进行拼接，适应性更强
    x = words_extend(x,4)
    return x

def words_extend(words_list, nums): # 对列表临近元素重组为新元素，从而进行列表拓展
    words_list_org = words_list.copy()
    nums = min(len(words_list_org), nums)
    for n in range(2, nums+1):
        temp_list = []
        for i in range(len(words_list_org)):
            try:
                temp_word = words_list_org[i]
                for k in range(1,n):
                    temp_word = temp_word + words_list_org[i+k]
                temp_list.append(temp_word)
            except:
                continue
        for m in temp_list:
            words_list.append(m)
    return words_list

def load_keywords(keywords_path):
    keywords_list = []
    class_words_list = []
    keywords_path_list = os.listdir(keywords_path)
    for m in keywords_path_list:
        keywords_file_path = os.path.join(keywords_path, m)
        class_words = m.split('_')[0]
        print('loading: ', keywords_file_path)
        for n in open(keywords_file_path):
            if not (n == '' or n == '\n'): # 删除空行，无效行
                if not n[:-1] in keywords_list: # 去重
                    keywords_list.append(n[:-1])
                    class_words_list.append(class_words)
    return keywords_list, class_words_list

def updata_keywords(updatawordsroot, keywords_path):
    newkeywords_list = []
    new_class_word_list = [] # 在此添加数据更新策略
    return newkeywords_list, new_class_word_list

def find_keywords(text, keywords_list, class_word_list):
    # 数据热更新
    new_keywords_list, new_class_word_list = updata_keywords(updatawordsroot, keywords_path)
    print(new_keywords_list)
    for n in range(len(new_keywords_list)):
        if not new_keywords_list[n] in keywords_list:
            keywords_list.append(new_keywords_list[n])
            class_word_list.append(new_class_word_list[n])
    # print(keywords_list)
    
    ## 敏感词检测
    # 基于jieba分词
    __seg_list = jieba.cut(text)
    _seg_list = "_".join(__seg_list)
    seg_list = _seg_list.split('_')
    seg_list = clean_str(seg_list) # 过滤无效字符
    print('分词结果： ', seg_list)
    # 遍历分词
    keywords_out = []
    class_words_out = []
    for words in seg_list:
        if words in keywords_list:
            index_ = keywords_list.index(words)
            class_word = class_word_list[index_]
            keywords_out.append(words)
            class_words_out.append(class_word)
    # 分析数据
    keywords_dict_list = []
    temp_keywords = []
    for n in keywords_out:
        if not n in temp_keywords:
            cnt = keywords_out.count(n)
            keywords_dict_list.append({n:cnt})
            temp_keywords.append(n)
        else:
            continue
    class_word_dict_list = []
    temp_class_word = []
    for m in class_words_out:
        if not m in temp_class_word:
            cnt2 = class_words_out.count(m)
            class_word_dict_list.append({m:(float(round(cnt2/len(class_words_out), 2)))})
            temp_class_word.append(m)
        else:
            continue
    return json.dumps({'sensitivewords':keywords_dict_list, 'class_count':class_word_dict_list})
        
def delkeywords(keywordspath, delkeywordspath, delkeyword):
    # 整理敏感词，建立文件让findwords重载keywords
    temp_keywords_list = []
    sign = -1
    keywordspath_list = os.listdir(keywordspath)
    for  n in keywordspath_list:
        keyword_file_path = os.path.join(keywordspath, n)
        for m in open(keyword_file_path):
            if m[:-1] == delkeyword:
                sign = 0
                continue
            else:
                temp_keywords_list.append(m[:-1])
        os.remove(keyword_file_path)
    txtkeywordspath = os.path.join(keywordspath, 'keywords.txt')
    with open(txtkeywordspath, 'w') as f:
        for k in temp_keywords_list:
            f.write(k)
            f.write('\n')
        f.close()
    txtsignpath = os.path.join(delkeywordspath, 'sign.txt')
    with open(txtsignpath, 'w') as f:
        f.write('sign')
        f.close()
    return sign, temp_keywords_list

keywords_path = './keywords/'
keywords_list = load_keywords(keywords_path)


import requests
from flask import Flask,render_template,request
import base64

def getRandomSet(bits):
    num_set = [chr(i) for i in range(48,58)]
    char_set = [chr(i) for i in range(97,123)]
    total_set = num_set + char_set
    value_set = "".join(random.sample(total_set, bits))
    return value_set

app = Flask(__name__)
imgroot = 'images'
updata_word_path = './updatawords'
updatawordsroot = 'updatawords'
delkeywordspath ='delkeywords'
keywords_path = 'keywords'

keywords_list, class_word_list = load_keywords(keywords_path)

@app.route("/findsensitivewords",methods = ['GET', 'POST'])
def findwords():
    if request.method == "POST":
        # base64data encode to iamge and save
        text = request.form.get('text')
        res = find_keywords(text, keywords_list, class_word_list)
        return res
    else:
        return "<h1>Find faces, please use post!</h1>"

@app.route("/upkeywords",methods = ['GET', 'POST'])
def upkeyword():
    if request.method == "POST":
        try:
            keyword = request.form.get('keyword')
            randname = getRandomSet(15)
            txtrandname = randname + '.txt'
            txtrandpath = os.path.join(updatawordsroot, txtrandname)
            with open(txtrandpath,'w') as f:
                f.write(keyword)
                f.write('\n')
                f.close()
            return {'sign':1} # write keyword scuessful
        except:
            print('>>>upkeywords error')
            return {'sign':-1}
    else:
        return "<h1>Updata keywords, please use post!</h1>"

@app.route("/delkeywords",methods = ['GET', 'POST'])
def del_keyword():
    if request.method == "POST":
        try:
            delkeyword = request.form.get('delkeyword')
            sign, _list = delkeywords(keywords_path, delkeywordspath, delkeyword)
            if sign == 0:
                return {'sign':sign, 'text':None} # delete sucuessful
            else:
                return {'sign':sign, 'text':_list} # delword is not in org keywords
        except:
            return {'sign':-2, 'text':None} # code error
    else:
        return "<h1>Delete keywords, please use post!</h1>"


if __name__ == '__main__':
    host = '0.0.0.0'
    port = '8879'
    app.run(debug=True, host=host, port=port)
