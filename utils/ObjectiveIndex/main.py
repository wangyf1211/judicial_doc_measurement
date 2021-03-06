# 裁判文书客观指标的检测
# input: 数据源为xml格式的裁判文书
# 输出直接显示在页面上，为错误信息提示
# 未确定如何打分

from xml.etree import ElementTree as etree
import re
import datetime, time

inputf = open('D:/NJU/final_project/data/example/100032.xml', 'r', encoding='utf-8')

xml_file = etree.parse("D:/NJU/final_project/data/example/100011.xml")
root_node = xml_file.getroot()[0]

# print(len(root_node))
#
# for node in root_node:
#     print(node.tag)

wenshu_content = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '其他': []}
wenshu_corr = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '其他': [], }
standard = ['文首', '首部', '事实', '理由', '依据', '主文', '尾部', '落款', '其他']


def wenshu_analysis(root_node):
    wenshu = {'文首': [], "首部": [], "事实": [], "理由": [], "依据": [], "主文": [], "尾部": [], '落款': [], '其他': [], '附件': []}
    # 第一次循环找到关键字节点
    test = []
    index = [-1 for i in range(9)]
    for i in range(len(root_node)):
        if root_node[i].tag == 'WS':
            wenshu['文首'].append(root_node[i])
            index[0] = i
        elif root_node[i].tag == 'DSR' or root_node[i].tag == 'SSJL':
            wenshu['首部'].append(root_node[i])
            index[1] = i
        elif root_node[i].tag == 'AJJBQK':
            wenshu['事实'].append(root_node[i])
            index[2] = i
        elif root_node[i].tag == 'CPFXGC':
            wenshu['理由'].append(root_node[i])
            index[3] = i
            for subnode in root_node[i]:
                if subnode.tag == 'FLFTYY':
                    wenshu['依据'].append(subnode)
                    index[4] = i
        elif root_node[i].tag == 'PJJG':
            wenshu['主文'].append(root_node[i])
            index[5] = i
            for subnode in root_node[i]:
                if subnode.tag == 'SSFCD':
                    index[6] = i
                    wenshu['尾部'].append(subnode)
        elif root_node[i].tag == 'WW':
            wenshu['落款'].append(root_node[i])
            index[7] = i
        elif root_node[i].tag == 'FJ':
            wenshu['附件'].append(root_node[i])
            index[8] = i
        else:
            test.append(i)
    print('结构事项顺序')
    print(index)
    for i in range(len(test)):
        if test[i] > (max(index)):
            wenshu['其他'].append(root_node[i])
        else:
            print('------未知错误')
            print(root_node[i].tag)
    return wenshu, index


# 结构事项准确性

def acc_GCSX(index, wenshu_corr):
    # 篇章结构规范性结果，0表示正确，1表示缺少，2表示顺序错误
    res = [0 for i in range(8)]
    for i in range(len(index)):
        if index[i] == -1:
            res[i] = 1
            wenshu_corr[standard[i]].append('篇章结构：缺少' + standard[i])
    lis_index = lis(index)
    # 最长递增子序列检测顺序
    for i in range(len(index)):
        if index[i] != -1 and (index[i] not in lis_index):
            wenshu_corr[standard[i]].append('篇章结构：' + standard[i] + '位置错误')
            res[i] = 2
    print('结构事项结果，0为正确，1为缺少，2为顺序错误')
    print(res)
    return res, wenshu_corr


# 最长递增子序列
def lis(arr):
    n = len(arr)
    m = [0] * n
    for x in range(n - 2, -1, -1):
        for y in range(n - 1, x, -1):
            if arr[x] < arr[y] and m[x] <= m[y]:
                m[x] += 1
        max_value = max(m)
        result = []
        for i in range(n):
            if m[i] == max_value:
                result.append(arr[i])
                max_value -= 1
    return result


# wenshu_analysis(root_node)

# 审理经过准确性
wenshu, _ = wenshu_analysis(root_node)


def acc_SLJG(wenshu, wenshu_corr):
    # 案件受理时间，开庭时间，适用程序，到庭情况，审理结果
    standard_SLJG = ['案件受理时间', '开庭时间', '适用程序', '到庭情况', '审理结果']
    index_SLJG = [-1 for i in range(5)]
    for node in wenshu['首部']:
        print(node.tag)
        if node.tag == 'SSJL':
            SSJL_txt = node.get('value')
            print('案件审理经过文本')
            print(SSJL_txt)
            for subnode in node:
                # 受理日期
                if subnode.tag == 'SLRQ':
                    index_SLJG[0] = SSJL_txt.find('受理')
                # 开庭日期
                if subnode.tag == 'KTRQ':
                    index_SLJG[1] = SSJL_txt.find('开庭')
                # 适用程序
                if '适用程序' in subnode.get('nameCN'):
                    index_SLJG[2] = SSJL_txt.find(subnode.get('value'))
                # 出庭当事人信息
                if subnode.tag == 'CTDSRXX':
                    index_SLJG[3] = SSJL_txt.find('到庭')
                index_SLJG[4] = SSJL_txt.find('审理终结')
            break
    print('案件审理经过顺序')
    print(index_SLJG)
    for i in range(len(index_SLJG)):
        if index_SLJG[i] == -1:
            wenshu_corr['首部'].append('案件审理经过缺少' + standard_SLJG[i])
    lis_index = lis(index_SLJG)
    for i in range(len(index_SLJG)):
        if index_SLJG[i] != -1 and (index_SLJG[i] not in lis_index):
            wenshu_corr['首部'].append('案件审理经过中' + standard_SLJG[i] + '顺序错误')
    print('案件审理经过累计错误')
    print(wenshu_corr['首部'])


def con_pun_DSR(DSR_txt, wenshu_corr):
    if re.match(r'^原告.*', DSR_txt):
        if DSR_txt[DSR_txt.index('原告') + 2] != '：':
            wenshu_corr['首部'].append('标点符号：' + DSR_txt + '原告后应为冒号')
    if re.match(r'^被告.*', DSR_txt):
        if DSR_txt[DSR_txt.index('被告') + 2] != '：':
            wenshu_corr['首部'].append('标点符号：' + DSR_txt + '被告后应为冒号')
    if re.match(r'^[\u4e00-\u9fa5]{0,6}人.*', DSR_txt):
        if DSR_txt[DSR_txt.index('人') + 1] != '：':
            wenshu_corr['首部'].append('标点符号：' + DSR_txt + '原告后应为冒号')
    return wenshu_corr


# 当事人信息准确性
def acc_DSR(wenshu, wenshu_corr):
    standard_DSR = ['诉讼身份', '姓名', '性别', '出生年月日', '民族', '籍贯', '住址', '公民身份证号']
    for node in wenshu['首部']:
        if node.tag == 'DSR':
            for subnode in node:
                # 没有加入YSF,DLR,QSF筛选
                DSR_txt = subnode.get('value')
                wenshu_corr = con_pun_DSR(DSR_txt, wenshu_corr)
                print('当事人信息')
                print(DSR_txt)
                index_DSR = [-1 for i in range(8)]
                for i in range(len(subnode)):
                    # 诉讼身份
                    if subnode[i].tag == 'SSSF':
                        if subnode[i].get('value') == '委托代理人':
                            wenshu_corr['首部'].append('委托代理人应更改为委托诉讼代理人')
                        index_DSR[0] = DSR_txt.index(subnode[i].get('value'))
                    # 诉讼参与人
                    elif subnode[i].tag == 'SSCYR':
                        index_DSR[1] = DSR_txt.index(subnode[i].get('value'))
                    # 单位职务分组
                    elif subnode[i].tag == 'DWZWFZ':
                        for tmp in subnode[i]:
                            if tmp.tag == 'ZW' and tmp.get('value') == '律师':
                                wenshu_corr['首部'].append('律师应更改为法律工作者')
                # 检测顺序
                lis_index = lis(index_DSR)
                for i in range(len(index_DSR)):
                    if index_DSR[i] != -1 and (index_DSR[i] not in lis_index):
                        wenshu_corr['首部'].append('当事人信息' + DSR_txt + '中' + standard_DSR[i] + '顺序错误')
        break
    print(wenshu_corr['首部'])


# acc_SLJG(wenshu, wenshu_corr)

# acc_DSR(wenshu,wenshu_corr)


# 事实描述简明性
# 对于过长的段落应该提示读者不应过长，但是怎么设定阈值未知
def con_pun_YGSCD(YGSCD_txt, wenshu_corr):
    pun_mao = [i.end() for i in re.finditer(r'.*原告(向本院提出)*诉讼请求(如下)*', YGSCD_txt)]
    for i in pun_mao:
        if YGSCD_txt[i] != '：':
            wenshu_corr['事实'].append('标点符号：原告诉讼请求后应为冒号')
    return wenshu_corr


def con_pun_BGBCD(BGBCD_txt, wenshu_corr):
    pun_mao = [i.end() for i in re.finditer(r'.*被告辩称(如下)*', BGBCD_txt)]
    for i in pun_mao:
        if BGBCD_txt[i] != '：':
            wenshu_corr['事实'].append('标点符号：被告辩称后应为冒号')
    return wenshu_corr


def con_pun_CMSSD(CMSSD_txt, wenshu_corr):
    pun_mao = [i.end() for i in re.finditer(r'.*本院认定(如下)*', CMSSD_txt)]
    for i in pun_mao:
        if CMSSD_txt[i] != '：':
            wenshu_corr['事实'].append('标点符号：本院认定后应为冒号')
    return wenshu_corr


def rea_SSMS(wenshu, wenshu_corr):
    # 案件基本情况
    AJJBQK = wenshu['事实'][0]
    AJJBQK_txt = AJJBQK.get('value')
    AJJBQK_len = len(AJJBQK_txt)
    AJJBQK_len, YGSCD_len, BGBCD_len, CMSSD_len, ZJD_len = 0
    for node in AJJBQK:
        # 原告诉称段
        if node.tag == 'YGSCD':
            YGSCD_txt = node.get('value')
            wenshu_corr = con_pun_YGSCD(YGSCD_txt, wenshu_corr)
            YGSCD_len = len(YGSCD_txt)
        # 被告辩称段
        elif node.tag == 'BGBCD':
            BGBCD_txt = node.get('value')
            wenshu_corr = con_pun_BGBCD(BGBCD_txt, wenshu_corr)
            BGBCD_len = len(BGBCD_txt)
        # 查明事实段
        elif node.tag == 'CMSSD':
            CMSSD_txt = node.get('value')
            wenshu_corr = con_pun_CMSSD(CMSSD_txt, wenshu_corr)
            CMSSD_len = len(CMSSD_txt)
        # 证据段
        elif node.tag == 'ZJD':
            ZJD_txt = node.get('value')
            ZJD_len = len(ZJD_txt)

    print(AJJBQK_len, YGSCD_len, BGBCD_len, CMSSD_len, ZJD_len)


# rea_SSMS(wenshu)


def con_pun_CPFXGC(CPFXGC_txt, wenshu_corr):
    if '本院认为' in CPFXGC_txt:
        if CPFXGC_txt[CPFXGC_txt.index('本院认为') + 4] != '，':
            wenshu_corr['理由'].appane('标点符号：本院认为后应该为逗号')
    return wenshu_corr


# 争议焦点条理性
def rea_ZYJD(wenshu, wenshu_corr):
    SSJL_txt = ''
    for node in wenshu['首部']:
        if node.tag == 'SSJL':
            SSJL_txt = node.get('value')
            break
    if '简易程序' in SSJL_txt:
        print('简易程序不需要争议焦点检测')
        return wenshu_corr
    CPFXGC_txt = wenshu['理由'][0].get('value')
    wenshu_corr = con_pun_CPFXGC(CPFXGC_txt, wenshu_corr)
    if not re.match(r'.*(争议焦点|本案焦点|焦点).*', CPFXGC_txt):
        wenshu_corr['理由'].append('未归纳案件争议焦点')
    print(wenshu_corr['理由'])
    return wenshu_corr


# rea_ZYJD(wenshu, wenshu_corr)


# 判断判决内容中标点符号使用一致性
def con_pun_PJJG(PJJG_txt, wenshu_corr):
    # 返回所有匹配的位置
    print(PJJG_txt)
    punc_mao = [i.start() for i in re.finditer(r'.*(判决|裁定)如下.*', PJJG_txt)]
    for punc in punc_mao:
        if PJJG_txt[punc + 4] != '：':
            wenshu_corr['主文'].append('标点错误：判决（裁定）如下后应该使用冒号')
    punc_fen = [i.start() for i in re.finditer(r'.*(二|三|四|五|六|七|八|九|十)、.*', PJJG_txt)]
    for punc in punc_fen:
        if PJJG_txt[punc - 1] != '；':
            wenshu_corr['主文'].append('标点错误：分项之前应该使用分号')
    punc_dun = [i.start() for i in re.finditer(r'.*(一|二|三|四|五|六|七|八|九|十)[^\w\u4e00-\u9fa5]+.*', PJJG_txt)]
    for punc in punc_dun:
        if PJJG_txt[punc + 1] != '、':
            wenshu_corr['主文'].append('标点错误：分项之后应该用顿号')

    return wenshu_corr


# 判决内容说明完整性
def com_PJNR(wenshu, wenshu_corr):
    # 判决金额，判决执行期限
    standard_PJNR = ['数量', '金额类型', '判决执行期限', '义务人']
    PJJG_node = wenshu['主文'][0]
    PJJG_txt = PJJG_node.get('value')
    wenshu_corr = con_pun_PJJG(PJJG_txt, wenshu_corr)
    # 判决结果中包不包含金额
    flag_ = 0
    for node in PJJG_node:
        # 判决结果内容
        if node.tag == 'PJJGNR':
            # 判决结果内容是不是涉及金额
            flag = 0
            PJJGNR_txt = node.get('value')
            print(PJJGNR_txt)
            index_PJNR = [-1 for i in range(4)]
            for subnode in node:
                if subnode.tag == 'PJJE':
                    for i in range(len(subnode)):
                        if subnode[i].tag == 'JE':
                            print('jine')
                            index_PJNR[0] = 1
                        elif subnode[i].tag == 'JELX':
                            index_PJNR[1] = 1
                    flag = 1
                    flag_ = 1
                if flag == 1 and subnode.tag == 'PJZXQX':
                    index_PJNR[2] = 1
                if flag == 1 and subnode.tag == 'YWR':
                    index_PJNR[3] = 1
            if flag == 1:
                print(index_PJNR)
                for i in range(4):
                    if index_PJNR[i] == -1:
                        wenshu_corr['主文'].append('判决内容说明完整性' + PJJGNR_txt + '中缺少' + standard_PJNR[i])
    if flag_ == 1 and not (re.match(r'.*如果未按本判决指的期间履行金钱给付义务，应当按照《中华人民共和国民事诉讼法》第二百五十三条的规定，加倍支付延迟履行期间的债务利息.*', PJJG_txt)):
        wenshu_corr['主文'].append('判决结果告知缺失')
    print(wenshu_corr['主文'])

    return wenshu_corr


# com_PJNR(wenshu, wenshu_corr)


# 诉费承担完整性
def com_SFCD(wenshu, wenshu_corr):
    SSFCD_node = wenshu['尾部'][0]
    # 是否多人承担诉讼费用
    count = 0
    # 诉讼费金额
    ssf_sum = 0
    ssf_item = 0
    for node in SSFCD_node:
        if node.tag == 'SSFCDJL':
            for subnode in node:
                # 诉讼费总金额
                if subnode.tag == 'SSFZJE':
                    ssf_sum = int(subnode.get('value').split('元')[0])
                if subnode.tag == 'SSFCDFZ':
                    # 承担人
                    for ssubnode in subnode:
                        if ssubnode.tag == 'CDR':
                            count += 1
                            for sssubnode in ssubnode:
                                if sssubnode.tag == 'CDJE':
                                    ssf_item += int(sssubnode.get('value').split('元')[0])
    if count > 1 and ssf_sum != ssf_item:
        wenshu_corr['尾部'].append('诉费承担完整性：未分别说明承担人各自承担金额')
    return wenshu_corr


# com_SFCD(wenshu, wenshu_corr)


# 加载案由列表
def load_ay():
    # 处理得到案由列表
    # ay_file = open('D:/NJU/final_project/data/anyou.txt', 'r', encoding='utf-8')
    # ay_out = open('D:/NJU/final_project/data/AY.txt', 'w', encoding='utf-8')
    # for line in ay_file.readlines():
    #     if '、' in line:
    #         ay_out.write(''.join(line.split('、',1)[1]))
    #     else:
    #         ay_out.write(line)
    # ay_file.close()
    # ay_out.close()
    ay_file = open('D:/NJU/final_project/data/AY.txt', 'r', encoding='utf-8')
    ay_list = []
    for line in ay_file.readlines():
        ay_list.append(line.split('\n')[0])
    ay_file.close()
    # print(ay_list)
    return ay_list


anyou_list = load_ay()


# 案由信息真实性
def aut_AY(root_node, wenshu_corr):
    ay_test = ''
    for node in root_node:
        if node.tag == 'SSJL':
            for subnode in node:
                if subnode.tag == 'AY':
                    ay_test = subnode.get('value')
                    break
            break
    if ay_test not in anyou_list:
        wenshu_corr['SSJL'].append('真实性：案由不在列表中，可能为编造案由')


# aut_AY(root_node,wenshu_corr)


# 裁判依据引用规范

def aut_CPYJ(wenshu, wenshu_corr):
    CPFXGC_node = wenshu['理由'][0]
    CPFXGC_txt = CPFXGC_node.get('value')
    if re.match(r'.*指导性文件.*', CPFXGC_txt):
        wenshu_corr['理由'].append('裁判依据引用规范：指导性文件不可做为判决依据')
    if re.match(r'.*会议纪要.*', CPFXGC_txt):
        wenshu_corr['理由'].append('裁判依据引用规范：会议纪要不可做为判决依据')
    if re.match(r'.*指导性案例.*', CPFXGC_txt):
        wenshu_corr['理由'].append('裁判依据引用规范：指导性案例不可做为判决依据')
    return wenshu_corr


# 日期转换函数
def date_change(date_txt):
    fmt = '%Y年%m月%d日'
    time_tuple = time.strptime(date_txt, fmt)
    year, month, day = time_tuple[:3]
    a_date = datetime.date(year, month, day)
    return a_date


# 案件信息延迟性，案件发生到立案日期
# 受理日期到结案日期
def del_date(root_node, wenshu_corr):
    date_list = []
    for node in root_node:
        if node.tag == 'SSJL':
            print('enen')
            for subnode in node:
                if subnode.tag == 'SLRQ':
                    print('jinlai')
                    SLRQ_txt = subnode.get('value')
                    date_SLRQ = date_change(SLRQ_txt)
                    break
        if node.tag == 'WW':
            for subnode in node:
                if subnode.tag == 'CPSJ':
                    for subsubnode in subnode:
                        if subsubnode.tag == 'CUS_JANYR':
                            JARQ_txt = subnode.get('value')
                            date_JARQ = date_change(JARQ_txt)
                    break
        if node.tag == 'CUS_SJ':
            for subnode in node:
                if subnode.tag == 'CUS_JTSJ':
                    date_list.append(date_change(subnode.get('value')))
    date_AJFS = min(date_list)
    print('案件发生时间，案件受理时间，案件结案时间')
    print(date_AJFS, date_SLRQ, date_JARQ)
    return wenshu_corr


# del_date(root_node, wenshu_corr)


# 全局唯一标识
# unique_id = 1

# 遍历所有的节点
def walkData(root_node, level, result_list):
    temp_list = [level, root_node.tag, root_node.attrib]
    result_list.append(temp_list)

    # 遍历每个子节点
    children_node = list(root_node)
    if len(children_node) == 0:
        return result_list
    for child in children_node:
        walkData(child, level + 1, result_list)
    return result_list


def met_CSRXX(root_node,wenshu_corr):
    for node in root_node:
        if node.tag=='DSR':
            CSR_count = []
            for subnode in node:
                if subnode.tag=='DLR' or subnode.tag=='QSF' or subnode.tag=='YSF':
                    result_list = []
                    level = 1
                    result_list = walkData(subnode,level,result_list)
                    CSR_count.append(len(result_list))
    print(CSR_count)
    return


met_CSRXX(root_node,wenshu_corr)


#事实描述部分细致性
def met_AJJBQK(wenshu,wenshu_corr):
    root = wenshu['事实'][0]
    result_list = []
    level = 1
    result_list = walkData(root, level, result_list)
    AJJBQK_count= len(result_list)
    print(AJJBQK_count)
    return AJJBQK_count

#理由部分细致性

def met_CPFXGC(wenshu,wenshu_corr):
    root = wenshu['理由'][0]
    result_list = []
    level = 1
    result_list = walkData(root, level, result_list)
    CPFXGC_count = len(result_list)
    print(CPFXGC_count)
    return CPFXGC_count

# met_AJJBQK(wenshu,wenshu_corr)
#
# met_CPFXGC(wenshu,wenshu_corr)