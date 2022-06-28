import pandas as pd
import csv


def convert_to_accent(code: str) -> str:
    """
    Converts the four-char code into accent in Chinese.
    xxxx represents 平上去入 respectively, with 0 indicating missing and 1
    indicating present.
    """

    a_lst = ['平', '上', '去', '入']
    a_txt = ''

    for index in range(len(code)):
        if code[index] == '1':
            a_txt = a_txt + a_lst[index]

    return a_txt


def get_complete_accents() -> list[str]:
    """
    Returns the complete list of accents.
    """

    lst = []

    for index in range(1, 16):
        bin_str = str(bin(index))[2:].rjust(4, '0')
        lst.append(convert_to_accent(bin_str[::-1]))

    return lst


def get_word_sets(f: 'TextIO') -> list[list]:
    """
    Get raw data in the form of lists with the first item being the word, and
    the second item being its associated value in numbers.
    """

    lst = []
    txt = ''
    
    for line in f:
        txt = txt + line.strip()
    txt = txt.strip('；')
    word_sets = txt.split('；')

    for word_set in word_sets:
        word = word_set[0:word_set.find('（')]
        num_1 = int(word_set[word_set.find('（') + 1:word_set.find('，')])
        num_2 = int(word_set[word_set.find('，') + 1:word_set.find('）')])
        num = num_1 + num_2
        lst.append([word, num])

    return lst


def get_dict_from_sheet(sheet: 'DataFrame') -> dict:
    """
    Converts sheet to a dictionary with entries as keys and (row, col)
    coordinates as values.
    """

    dict = {}
    row_count = len(sheet)
    col_count = len(sheet.columns)

    for row in range(row_count):
        for col in range(col_count):
            entry = sheet.iloc[row, col]
            if not pd.isna(entry):
                dict[entry] = (row, col)

    return dict


def sort_data(word_sets: list[list], sheet: 'DataFrame', rule: dict) -> dict:
    dict = {}
    for set in word_sets:
        prev_word = set[0]
        sort_word = ''
        sort_type = '0000'
        for char in prev_word:
            pos = rule[char]
            sort_word = sort_word + sheet.iloc[pos[0], 0]
            sort_type = sort_type[:pos[1]] + '1' + sort_type[pos[1] + 1:]

        if sort_word not in dict:
            dict[sort_word] = {}
        sort_dict = dict[sort_word]

        sort_type = convert_to_accent(sort_type)

        if sort_type not in sort_dict:
            sort_dict[sort_type] = set[1]
        else:
            sort_dict[sort_type] += set[1]
    return dict


raw_data_path = 'test3.txt'  # 需要统计的文件
data_sheet_path = 'table.csv'  # 保存转换规则的表格
output_path = 'result.csv'  # 保存统计结果的文件
with open(raw_data_path, encoding='utf-8') as f:
    word_sets = get_word_sets(f)
data_sheet = pd.read_csv(data_sheet_path)

conv_rule = get_dict_from_sheet(data_sheet)
sorted_dict = sort_data(word_sets, data_sheet, conv_rule)

sorted_lst = []
for key in sorted_dict:
    word_dict = {}
    word_dict['归类'] = key
    for word_key in sorted_dict[key]:
        word_dict[word_key] = sorted_dict[key][word_key]
    sorted_lst.append(word_dict)

fields = ['归类'] + get_complete_accents()
with open(output_path, 'w') as csv_f:
    writer = csv.DictWriter(csv_f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(sorted_lst)

content_lst = []
with open(output_path, 'r') as f:
    for line in f:
        if not line.isspace():
            content_lst.append(line)

with open(output_path, 'w') as f:
    f.writelines(content_lst)
