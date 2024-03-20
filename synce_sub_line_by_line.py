import configparser
import pysubs2
import re
import requests
import textdistance
from os import system
from sys import exit
from os.path import isfile, join, splitext

import PySimpleGUI as sg
from symspellpy import SymSpell, Verbosity

sym_spell = SymSpell()
# dictionary_path = "C:\\Users\\GIANG\\Downloads\\Simple-ocr-hardsubs-main\\merge.txt"
# sym_spell.load_dictionary(dictionary_path, 0, 1, encoding = "utf8")

dictionary_path = join("dictionaries", "vi_full.txt")
sym_spell.load_dictionary(dictionary_path, 0, 1, encoding="utf8")
dictionary_path = join("dictionaries", "romanji.txt")
sym_spell.load_dictionary(dictionary_path, 0, 1, encoding="utf8")
dictionary_path = join("dictionaries", "enamdict.txt")
sym_spell.load_dictionary(dictionary_path, 0, 1, encoding="cp932")

# try:  
# 	req = requests.get("https://anotepad.com/notes/ca7d4apf")
# 	if "Allow" in req.text:
# 		pass
# 	else:
# 		print("Too old to work :v ")
# 		exit()
# except:
# 	print("Too old to work :v ")
# 	exit()


config = configparser.ConfigParser()
config.read('config.ini', encoding = "utf8")

def get_para_from_recent(default = False):
	if default:
		parameter = dict(config["Default"])
	else:
		parameter = dict(config["Recent"])
	for k in parameter.keys():
		if parameter[k] in ["True", "False"]:
			parameter[k] = bool(parameter[k])
		elif parameter[k].replace(".","").isdigit():
			if "." not in parameter[k]:
				parameter[k] = int(parameter[k])
			else:
				parameter[k] = float(parameter[k])
	return parameter
parameter = get_para_from_recent()

# parameter[
#     "origin_sub_path"] = ("C:\\Users\\GIANG\\Downloads\\Simple-ocr-hardsubs-main\\[MTBB] The Dangers in My Heart S2 - "
#                           "07 (WEB 1080p) [83A9681F]_Track03.ass")
# parameter[
#     "ocr_sub_path"] = ("C:\\Users\\GIANG\\Downloads\\Simple-ocr-hardsubs-main\\Tập 07 Boku no Kokoro no Yabai Yatsu "
#                        "Season 2 (The Dangers in My Heart Season 2, Bokuyaba) 2024 HD-VietSub.srt")

# parameter[
#     "origin_audio_path"] = ("C:\\Users\\GIANG\\Downloads\\Simple-ocr-hardsubs-main\\[MTBB] The Dangers in My Heart S2 "
#                             "- 07 (WEB 1080p) [83A9681F].mkv")
# parameter[
#     "ocr_audio_path"] = ("C:\\Users\\GIANG\\Downloads\\Simple-ocr-hardsubs-main\\Tập 07 Boku no Kokoro no Yabai Yatsu "
#                          "Season 2 (The Dangers in My Heart Season 2, Bokuyaba) 2024 HD-VietSub.mp4")

# parameter["output_filename"] = "Output.ass"

# Define the window's contents
layout = [[sg.Text("Synced sub: "), 
           sg.Input(key="origin_sub_path", change_submits=True, expand_x=True, default_text=parameter["origin_sub_path"]),
           sg.FileBrowse(key='origin_sub_path')],
          [sg.Text("ocr sub: "),
           sg.Input(key="ocr_sub_path", change_submits=True, expand_x=True, default_text=parameter["ocr_sub_path"]),
           sg.FileBrowse(key='ocr_sub_path')],

          [sg.Text("Audio of synced sub: "), sg.Input(key="origin_audio_path", change_submits=True, expand_x=True, default_text=parameter["origin_audio_path"]),
           sg.FileBrowse(key='origin_audio_path')],
          [sg.Text("Audio of ocr sub: "),
           sg.Input(key="ocr_audio_path", change_submits=True, expand_x=True, default_text=parameter["ocr_audio_path"]),
           sg.FileBrowse(key='ocr_audio_path')],
          [sg.Text("Output: "), sg.Input(key="output_filename", expand_x=True, default_text=parameter["output_filename"])],
          # [sg.Input(key='INPUT')],
          [sg.Checkbox(text="Using sushi to normalized_similarity: ", key="is_using_sushi", default=parameter["is_using_sushi"])],
          [sg.Checkbox(text="Comment from_eng sub", key="comment_eng_sub", default=parameter["comment_eng_sub"])],
          [sg.Checkbox(text="Comment from_ocr sub", key="comment_ocr_sub", default=parameter["comment_ocr_sub"])],
          [sg.Checkbox(text="Try translate sign", key="trans_sign", default=parameter["trans_sign"])],
          [sg.Text("same_rate: "), sg.Spin([ig / 100 for ig in range(101)], parameter["same_rate"], key="same_rate", size=(20, 1))],
          [sg.Text("distance_string_rate: "),
           sg.Spin([ig / 100 for ig in range(101)], parameter["distance_string_rate"], key="distance_string_rate",size=(20, 1))],
          [sg.Text("distance_string_character: "),
           sg.Spin([ig for ig in range(10)], parameter["distance_string_character"], key="distance_string_character",size=(20, 1))],
          [sg.Text("framerate: "), sg.Input(key="framerate", size=(20, 1), default_text=parameter["framerate"])],
          [sg.Text("frame_distance: "),
           sg.Spin([ig for ig in range(10)], parameter["frame_distance"], key="frame_distance", size=(20, 1))],
          # [sg.Text("same_rate: "), sg.Input(key="same_rate", expand_x=True, default_text = parameter["same_rate"])],
          [sg.Text(size=(40, 1), key='log')],
          [sg.Button('Reset setting'), sg.Push(), sg.Button('Ok', size=(20, 1)), sg.Button('Quit')]]

# Create the window
window = sg.Window('Sub_sync code by luudanmatcuoi ver 1.2', layout,icon='dango.ico')

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()
    # See if user wants to quit or window was closed
    if event == sg.WINDOW_CLOSED or event == 'Quit':
        exit()
    # Output a message to the window
    # window['OUTPUT'].update('Hello ' + values['INPUT'] + "! Thanks for trying PySimpleGUI")
    if event == "Reset setting":
        parameter = get_para_from_recent(default = True)
        for ta in parameter.keys():
            try:
                values[ta]
                window[ta].update(parameter[ta])
            except:
                pass

    if event == "Ok":
        # Load values from GUI -> parameter
        # for ta in parameter.keys():
        #     if ta in values.keys():
        #         if type(parameter[ta]) == type(True):
        #         	parameter[ta] = bool(values[ta])
        #         elif type(parameter[ta]) == type(1):
        #         	parameter[ta] = int(values[ta])
        #         elif type(parameter[ta]) == type(1.1):
        #         	parameter[ta] = float(values[ta])
        #         else:
        #         	parameter[ta] = values[ta]

        for ta in parameter.keys():
            if ta in values.keys():
                if values[ta] in ["True", "False"]:
                	parameter[ta] = bool(values[ta])
                else:
                	try:
	                	parameter[ta] = int(values[ta])
	                except:
	                	if len(re.findall(r"[0-9]+/[0-9]+",values[ta]))>0:
	                		parameter[ta] = int(values[ta].split("/")[0])/int(values[ta].split("/")[1])
	                	else:
		                	try:
		                		parameter[ta] = float(values[ta])
		                	except:
		                		try:
		                			parameter[ta] = str(values[ta])
		                		except:
		                			pass
        print(parameter)
        # Check output_filename var
        pre, ext = splitext(parameter["output_filename"])
        parameter["output_filename"] = pre + ".ass"

        # Save setting to recent
        config["Recent"] = parameter
        with open('config.ini', 'w', encoding = "utf8") as configfile:
            config.write(configfile)

        if isfile(parameter["origin_sub_path"]) and isfile(parameter["ocr_sub_path"]) and not parameter[
            "is_using_sushi"] or (isfile(parameter["origin_sub_path"]) and isfile(parameter["ocr_sub_path"]) and
                                  isfile(parameter["origin_audio_path"]) and isfile(parameter["ocr_audio_path"])):
            window["log"].update("Please wait...")
            break
        else:
            window["log"].update("Wrong path, please try again")
            continue


def split_line(stri):
    temp_split_line = re.sub(r"^\\N {0,5}([a-z0-9đóòỏõọôốồổỗộơớờởỡợáàảãạâấầẩẫậăắằẳẵặêếềểễệéèẻẽẹúùủũụưứừửữựíìỉĩịýỳỷỹỵ])",
                             r" \1",
                             stri)
    temp_split_line = temp_split_line.replace("\\N", "]")
    # Chia các mảng từ
    temp_split_line = re.findall(
        r"[^!\"#$%&\\\'()*+,\-./:;<=>?@\[\\]^_`{|}~]+|[!\"#$%&\\\'()*+,\-./:;<=>?@\[\\\\\]^_`{|}~]", temp_split_line)
    # Các mảng từ có chứa dấu câu
    text_index = [temp_split_line.index(a) for a in temp_split_line if not any(
        t in a for t in r"\!\"\#\$\%\&\\\'\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\\\]\^\_\`\{\|\}\~") and len(a) > 0]
    print(text_index)
    print(stri)

    if len(text_index) <= 1:
        result = [stri]
        return result
    else:
        # result = ["".join(temp[:text_index[1]])]
        # for tex in range(1,len(text_index)):
        # 	if tex<len(text_index)-1:
        # 		result+=["".join(temp[text_index[tex]:text_index[tex+1]])]
        # 	else:
        # 		result+=["".join(temp[text_index[tex]:])]
        result = ["".join(temp_split_line[:text_index[1]]), "".join(temp_split_line[text_index[1]:])]
        for i in range(len(result)):
            result[i] = result[i].replace("]", "").lstrip().rstrip()
        return result


def cal_same_time(line1, line2):
    start1, end1 = line1.start, line1.end
    start2, end2 = line2.start, line2.end
    temp = (abs(start1 - end1) + abs(start2 - end2) - abs(start1 - start2) - abs(end1 - end2)) // 2
    if temp < 0:
        return 0
    else:
        return temp


def duration(line):
    return line.end - line.start


def is_same_sub(a, b):
    if (textdistance.hamming.distance(a, b) >= parameter["distance_string_character"] and
            textdistance.hamming.normalized_similarity(a, b) <= parameter["distance_string_rate"]):
        return False
    else:
        return True


def is_same_time(a, b):
    if a is None or b is None:
        return False
    if abs(a.start - b.start) >= 1000 / parameter["framerate"] * parameter["frame_distance"] or abs(
            a.end - b.end) >= 1000 / parameter["framerate"] * parameter["frame_distance"]:
        return False
    else:
        return True


def is_continue_time(a, b):
    if abs(a.end - b.start) < 1000 / parameter["framerate"] * parameter["frame_distance"]:
        return True
    else:
        False


def apply_sub(a_line, text):
    if type(a_line) == type([]) and len(a_line) == 1:
        a_line = a_line[0]
    if type(text) != type("") and type(text) != type([]):
        text = text.text
    elif type(text) == type([]) and len(text) == 1:
        text = text[0].text
    temp = re.sub(r"\{([^\\]+)}", r"[\1]", a_line.text)

    match = re.findall(r"(({[^{}]+})?([^{}]+)?({[^{}]+})?)+", temp)
    temp = ""
    for t in match:
        for m in t:
            if m == "":
                pass
            elif "{" in m:
                temp += m
            elif "{" not in m:
                if parameter["apply_mode"] == "comment":
                    temp += "{" + m + "}"
                else:
                    pass
    text = temp + text
    a_line.text = text
    return a_line


def combine_sub(a_group, b_group):
    # Ghép các sub giống nhau hiển thị liên tiếp
    i = 0
    while i + 1 < len(b_group):
        if b_group[i + 1] is None: break
        if is_same_sub(b_group[i].text, b_group[i + 1].text) and is_continue_time(b_group[i], b_group[i + 1]):
            b_group[i].end = b_group[i + 1].end
            del b_group[i + 1]
        else:
            i += 1

    # Combine nếu sub gốc có \\N -> Ghép vào cx \\N nếu không ghép bằng dấu cách
    if "\\N" in a_group[0].text and len(b_group) > 1:
        b_group[0].text = "\\N".join([t.plaintext for t in b_group])
        b_group = [b_group[0]]
    elif "\\N" not in a_group[0].text and len(b_group) > 1:
        b_group[0].text = " ".join([t.plaintext for t in b_group])
        b_group = [b_group[0]]

    if len(b_group) == 1:
        a_group[0] = apply_sub(a_group[0], b_group[0].text)
        a_group[0].name = "combine"

    return a_group


def split_sub(a_group, b_group):
    # Thử split sub theo quy trình
    split = split_line(b_group[0].text)
    for q in range(len(split) - len(b_group)):
        b_group += [b_group[0].copy()]
    for q in range(len(b_group)):
        b_group[q].text = split[q]

    ste = len(b_group)
    for q in range(len(a_group) - len(b_group)):
        b_group += [a_group[q + ste].copy()]
        b_group[-1].text = ""

    if parameter["quit_split_line_section"]:
        for blablo in range(len(a_group)):
            a_group[blablo] = apply_sub(a_group[blablo], b_group[blablo])
        return a_group

    # Open window
    text_width = 45
    a_group_list = [[sg.Text("Synced sub")]] + [[sg.Multiline(key=f"a_group_{t}",
                                                              size=(text_width, len(a_group[t].text) // text_width + 2),
                                                              default_text=a_group[t].text, disabled=True)] for t in
                                                range(len(a_group))]
    b_group_list = [[sg.Text("OCR sub")]] + [[sg.Multiline(key=f"b_group_{t}",
                                                           size=(text_width, len(b_group[t].text) // text_width + 2),
                                                           default_text=b_group[t].text)] for t in range(len(b_group))]
    split_layout = [[sg.Column(a_group_list), sg.VSeperator(), sg.Column(b_group_list), ],
                    [sg.Push(), sg.Button('Swap'), sg.Button('Combine'), sg.Button('Duplicate'),
                     sg.Button('Copy eng_sub')],
                    [sg.Push(), sg.Push(), sg.Push(), sg.Button('Ok'), sg.Button('Cancel'), sg.Push(), sg.Push(),
                     sg.Button('Quit section')]
                    ]
    split_window = sg.Window('Sub_sync code by luudanmatcuoi', split_layout, finalize=True)
    split_window.bind("<Escape>", "ESCAPE")

    while True:
        event, values = split_window.read()
        # See if user wants to quit or window was closed
        if event in (sg.WINDOW_CLOSED, "ESCAPE", "Cancel"):
            split_window.close()
            return a_group
        if event == "Quit section":
            parameter["quit_split_line_section"] = True
            split_window.close()
            for g in range(len(a_group)):
                a_group[g] = apply_sub(a_group[g], b_group[g])
            return a_group
        if event == "Swap":
            temp_swap = values[f"b_group_0"]
            e = 1
            while True:
                try:
                    split_window[f"b_group_{e - 1}"].update(values[f"b_group_{e}"])
                    e += 1
                except:
                    split_window[f"b_group_{e - 1}"].update(temp_swap)
                    break
        if event == "Combine":
            temp_comb = values[f"b_group_0"]
            e = 1
            while True:
                try:
                    temp_comb += " " + values[f"b_group_{e}"]
                    e += 1
                except:
                    break
            split_window[f"b_group_0"].update(temp_comb)
            e = 1
            while True:
                try:
                    values[f"b_group_{e}"]
                    split_window[f"b_group_{e}"].update("")
                    e += 1
                except:
                    break
        if event == "Duplicate":
            temp_dup = values[f"b_group_0"]
            e = 1
            while True:
                try:
                    values[f"b_group_{e}"]
                    split_window[f"b_group_{e}"].update(temp_dup)
                    e += 1
                except:
                    break
        if event == "Copy eng_sub":
            e = 0
            while True:
                try:
                    values[f"b_group_{e}"]
                    split_window[f"b_group_{e}"].update(values[f"a_group_{e}"])
                    e += 1
                except:
                    break
        if event == "Ok":
            e = 0
            a_group_result = []
            while f"a_group_{e}" in values.keys():
                a_group_result += [values[f"a_group_{e}"]]
                e += 1
            e = 0
            b_group_result = []
            while f"b_group_{e}" in values.keys():
                temp = values[f"b_group_{e}"]
                if len(temp) >= 1:
                    if " " == temp[0]: temp = temp[1:]
                    if " " == temp[-1]: temp = temp[:-1]
                    if "\n" == temp[-1]: temp = temp[:-1]
                b_group_result += [temp]
                e += 1

            for i in range(len(a_group_result)):
                a_group[i] = apply_sub(a_group[i], b_group_result[i])
            break
    split_window.close()
    for i in range(len(a_group)):
        a_group[i].name = "split"
    return a_group


def check_spelling(stri):
    toteti = stri.replace("0", "").replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5",
                                                                                                               "").replace(
        "6", "").replace("7", "").replace("8", "").replace("9", "")
    if len(toteti) == 0:
        return [stri, True]

    suggestions = sym_spell.lookup(stri.lower(),
                                   Verbosity.CLOSEST, max_edit_distance=2, include_unknown=True)
    result = suggestions[0]
    if result.term.lower() == stri.lower():
        return [stri, True]
    else:
        if stri[0].isupper():
            if any(ext in stri for ext in
                   "đóòỏõọôốồổỗộơớờởỡợáàảãạâấầẩẫậăắằẳẵặêếềểễệéèẻẽẹúùủũụưứừửữựíìỉĩịýỳỷỹỵĐÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÊẾỀỂỄỆÉÈẺẼẸÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴ"):
                result.term = result.term[0].upper() + result.term[1:]
                return [result.term, False]
            else:
                return [stri, True]
        else:
            return [result.term, False]


##########################################################################################
#### ----------------------------------------START ----------------------------------#####
##########################################################################################


if parameter["is_using_sushi"]:
    system(
        'sushi.exe --src "{ocr_audio_path}" --dst "{origin_audio_path}" --script "{ocr_sub_path}" -o ocr_sushi.srt'.format(
            **parameter))
    ocr_sub_sushi_path = "ocr_sushi.srt"
else:
    ocr_sub_sushi_path = parameter["ocr_sub_path"]

# Load 2 file
eng_sub = pysubs2.load(parameter["origin_sub_path"])
ocr_sub = pysubs2.load(ocr_sub_sushi_path)

# Nhặt tất cả sign dialogue ra khỏi eng_sub
sign_group = []
i_eng = 0
while i_eng < len(eng_sub):
    if any(["\\" + tag + "(" in eng_sub[i_eng].text for tag in ["pos", "mov", "org", "clip"]]) and not eng_sub[
        i_eng].is_comment:
        eng_sub[i_eng].name = "sign"
        sign_group += [eng_sub[i_eng]]
        del eng_sub[i_eng]
    else:
        i_eng += 1
# Nhận diện layer thường sử dụng
layer_eng_sub = [eng.layer for eng in eng_sub]
layer_eng_sub = max(set(layer_eng_sub), key=layer_eng_sub.count)

# Filter sub ocr : Loại bỏ sub trống, filter chính tả, cảnh báo các ký tự lạ
f = open('filter_rules.txt', "r", encoding="utf8")
rules = [g.replace("\\n", "\\\\N") for g in f.read().split("\n") if len(g) > 0]
rules = [g.split("________") for g in rules if "#" not in g[0]]
f.close()
i_ocr = 0
while i_ocr < len(ocr_sub):
    for r in rules:
        if r[0] == "replace":
            if "\\u" in r[1]:
                abcds = re.findall(r"\\u[0-9ABCDEFabcdef]{2,4}", r[1])
                for abcd in abcds:
                    r[1] = r[1].replace(abcd, chr(int(abcd[2:], 16)))
            if "\\u" in r[2]:
                abcds = re.findall(r"\\u[0-9ABCDEFabcdef]{2,4}", r[2])
                for abcd in abcds:
                    r[2] = r[2].replace(abcd, chr(int(abcd[2:], 16)))
            ocr_sub[i_ocr].text = ocr_sub[i_ocr].text.replace(r[1], r[2])
        elif r[0] == "replace_word":
            ocr_sub[i_ocr].text = re.sub(r"\b" + r[1] + r"\b", r[2], ocr_sub[i_ocr].text)
        else:
            ocr_sub[i_ocr].text = re.sub(r[1], r[2], ocr_sub[i_ocr].text)
    # Print cảnh báo các ký tự lạ
    match = re.findall(
        r"[^0-9a-zA-Z\s\WđóòỏõọôốồổỗộơớờởỡợáàảãạâấầẩẫậăắằẳẵặêếềểễệéèẻẽẹúùủũụưứừửữựíìỉĩịýỳỷỹỵĐÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÊẾỀỂỄỆÉÈẺẼẸÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴ]",
        ocr_sub[i_ocr].text)
    if len(match) > 0 and "OCR_EMPTY_RESULT" not in ocr_sub[i_ocr].text:
        print("Caution unexpected characters:\t" + " ".join(match) + "\t" + ocr_sub[i_ocr].text)

    # Loại bỏ các line có 60-90% là các ký tự lạ
    tempa = ocr_sub[i_ocr].text.split("\\N")
    tempb = "dfasdfaergsergdzf".join(tempa).split("dfasdfaergsergdzf")
    for t in range(len(tempa)):
        tempa[t] = re.sub(
            r"[^0-9a-zA-Z\s\WđóòỏõọôốồổỗộơớờởỡợáàảãạâấầẩẫậăắằẳẵặêếềểễệéèẻẽẹúùủũụưứừửữựíìỉĩịýỳỷỹỵĐÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÊẾỀỂỄỆÉÈẺẼẸÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴ]",
            "", tempa[t])
        ga = tempa[t].replace(" ", "")
        gb = tempb[t].replace(" ", "")
        if len(ga) < len(gb) * (1 - 60 / 100):
            tempb[t] = ""
    tempb = list(filter(None, tempb))
    if len(tempb) == 0:
        del ocr_sub[i_ocr]
        continue
    ocr_sub[i_ocr].text = "\\N".join(tempb)

    # Loại bỏ sub có chữ ocr_empty_text
    if "OCR_EMPTY_RESULT" in ocr_sub[i_ocr].text:
        del ocr_sub[i_ocr]
        continue
    else:
        i_ocr += 1

###Block phát hiện và sửa lỗi chính tả.
line_need_correction = []
for i_ocr in range(len(ocr_sub)):
    # Chia thành các mảng
    temp = re.findall(
        r"|[^\s!\"#$%&\\\'()*+,\-./:;<=>?@\[\\\\\]^_`{|}~]+|[ \s!\"#$%&\\\'()*+,\-./:;<=>?@\[\\\\\]^_`{|}~]",
        ocr_sub[i_ocr].text.replace("\\N", "\n"))
    for t in range(len(temp)):
        # Lọc các word có 1 ký tự
        if len(temp[t]) == 1 and re.search(
                r"[a-zA-Z0-9\s!\"#$%&\\\'()*+,\-./:;<=>?@\[\\\\\]^_`{|}~đóòỏõọôốồổỗộơớờởỡợáàảãạâấầẩẫậăắằẳẵặêếềểễệéèẻẽẹúùủũụưứừửữựíìỉĩịýỳỷỹỵĐÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÊẾỀỂỄỆÉÈẺẼẸÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴ]",
                temp[t]):
            # Các word 1 ký tự là dấu câu hoặc số
            if re.search(
                    r"[\s()\"!,\-.;?_~a-zA-Z0-9đóòỏõọôốồổỗộơớờởỡợáàảãạâấầẩẫậăắằẳẵặêếềểễệéèẻẽẹúùủũụưứừửữựíìỉĩịýỳỷỹỵĐÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÁÀẢÃẠÂẤẦẨẪẬĂẮẰẲẴẶÊẾỀỂỄỆÉÈẺẼẸÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴ]",
                    temp[t]):
                temp[t] = [temp[t], True]
            else:
                temp[t] = [temp[t], False]
        else:
            sug = check_spelling(temp[t])
            # if not sug[1]:
            # 	print(temp[t])
            temp[t] = sug

    temp_res = len(temp) - sum([int(g[1]) for g in temp])
    if temp_res > 0:
        line_need_correction += [[i_ocr, temp, ocr_sub[i_ocr].text]]

# line_need_correction = []
# temp_sym = []
# for i_ocr in range(len(ocr_sub)):
# 	stri = ocr_sub[i_ocr].text.replace("\\N","\n")

# 	temp = sym_spell.lookup_compound(stri, max_edit_distance=2, ignore_non_words=True, transfer_casing =True )

# 	# print(temp, "\t\t\t\t" , ocr_sub[i_ocr].text)
# 	temp = temp[0].term
# 	if len(temp_sym) < len(sym_spell.replaced_words):
# 		print(sym_spell.replaced_words)
# 		for key in sym_spell.replaced_words.keys():
# 			if key in temp_sym:
# 				continue
# 			print(key)
# 			# line_need_correction+=[ i_ocr,[temp, False] ,ocr_sub[i_ocr].text]
# 			print(temp, "\t\t\t\t" , ocr_sub[i_ocr].text)
# 		temp_sym = sym_spell.replaced_words.keys()


spelling_layout = [[sg.Push(), sg.Text('Double check pls...'), sg.Push()],
                   [sg.Multiline(key=f"spelling", size=(70, 20), default_text="")],
                   [sg.Push(), sg.Button('Ok'), sg.Button('Quit'), sg.Push()]]

spelling_window = sg.Window('Spelling check', spelling_layout, finalize=True)
spelling_window.bind("<Escape>", "ESCAPE")

for lin in line_need_correction:
    spelling_window['spelling'].print(f"[{lin[0]}]", end='', text_color='black')
    spelling_window['spelling'].print('\n', end='')
    spelling_window['spelling'].print(f"[{lin[2]}]", end='', text_color='grey60')
    spelling_window['spelling'].print('\n', end='')
    for sp in lin[1]:
        if sp[1]:
            spelling_window['spelling'].print(sp[0], end='', text_color='black')
        else:
            spelling_window['spelling'].print(sp[0], end='', text_color='red')
    spelling_window['spelling'].print('\n\n', end='')

while True:
    event, values = spelling_window.read()
    # See if user wants to quit or window was closed
    if event in (sg.WINDOW_CLOSED, "ESCAPE", "Quit"):
        spelling_window.close()
        break
    if event == "Ok":
        data_spelling = values[f"spelling"].replace("\r", "")
        data_spelling = re.findall(r"\[([0-9]+)](\n\[[^]\[]+])?\n([^\[\]]+)", data_spelling + "\n\n")

        for da in data_spelling:
            temp_da = [dq for dq in da if "[" not in dq and "]" not in dq and dq != "\n"]
            if len(temp_da) == 0:
                temp_da = ""
            else:
                temp_da = max(temp_da, key=len)
            ocr_sub[int(da[0])].text = temp_da.lstrip().rstrip().replace("\n", "\\N")
        # print(ocr_sub[int(da[0])].text)
        spelling_window.close()
        break

i_ocr = 0
while i_ocr < len(ocr_sub):
    if ocr_sub[i_ocr] == "":
        del ocr_sub[i_ocr]
    else:
        i_ocr += 1

# Change time stamp
temp_eng_time = [t.copy() for t in eng_sub if t.is_comment is False]
temp_eng_time = sorted(temp_eng_time, key=lambda t: t.start)
for i in range(len(ocr_sub)):
    for t in range(len(temp_eng_time) - 1):
        if is_continue_time(temp_eng_time[t], temp_eng_time[t + 1]) \
                and ocr_sub[i].start < temp_eng_time[t].end < ocr_sub[i].end \
                and 1 - abs(
            1 - cal_same_time(temp_eng_time[t], ocr_sub[i]) / cal_same_time(temp_eng_time[t + 1], ocr_sub[i])) > \
                parameter["soft_combine_rate"]:
            ocr_sub[i].start = temp_eng_time[t].start
            ocr_sub[i].end = temp_eng_time[t + 1].end
# print(ocr_sub[i].text)

# Link tất cả các sub với nhau -> lưu vào group
group = []
for ocr_line in ocr_sub:
    is_has_engsub_group = False
    for eng_line in eng_sub:
        if eng_line.is_comment: continue
        same_time = cal_same_time(eng_line, ocr_line)
        if same_time > duration(eng_line) * parameter["same_rate"] or same_time > duration(ocr_line) * parameter[
            "same_rate"]:
            group += [{"start": eng_line.start, "end": eng_line.end, "eng": eng_line, "ocr": ocr_line}]
            is_has_engsub_group = True
    if not is_has_engsub_group:
        group += [{"start": ocr_line.start, "end": ocr_line.end, "eng": None, "ocr": ocr_line}]

for eng_line in eng_sub:
    if eng_line.is_comment:
        group += [{"start": eng_line.start, "end": eng_line.end, "eng": eng_line, "ocr": None}]
        continue
    is_has_engsub_group = False
    for ocr_line in ocr_sub:
        same_time = cal_same_time(ocr_line, eng_line)
        if same_time > duration(ocr_line) * parameter["same_rate"] or same_time > duration(eng_line) * parameter[
            "same_rate"]:
            is_has_engsub_group = True
    if not is_has_engsub_group:
        group += [{"start": eng_line.start, "end": eng_line.end, "eng": eng_line, "ocr": None}]

group = sorted(group, key=lambda d: d['start'])

# xử lý các case
i_group = 0
best_subtitle = []
while i_group < len(group):
    a = []
    b = []
    if group[i_group]["eng"] is not None:
        a += [group[i_group]["eng"]]

    if group[i_group]["ocr"] is not None:
        b += [group[i_group]["ocr"]]

    # Check Following group xem có trùng engline hay ocr line không ?
    following = 1
    while True:
        temp_i = i_group + following
        if temp_i == len(group):
            break
        # Nếu bên a/b rỗng -> sub chỉ từ 1 bên eng/ocr -> dừng lặp
        if len(a) == 0 or len(b) == 0:
            break

        # Tìm kiếm sub chung -> đưa về a/b
        if group[temp_i]["eng"] == a[0] and group[temp_i]["ocr"] != b[0] and group[temp_i]["ocr"] is not None:
            b += [group[temp_i]["ocr"]]
        elif group[temp_i]["eng"] != a[0] and group[temp_i]["ocr"] == b[0] or is_same_time(group[i_group]["eng"],
                                                                                           group[temp_i]["eng"]):
            a += [group[temp_i]["eng"]]
        else:
            break
        following += 1
    i_group += following

    # Chia a và b vào các trường hợp
    if len(a) == 0:
        for i in range(len(b)):
            b[i].name = "from_ocr"
            b[i].layer = layer_eng_sub
            b[i].type = "Comment"
        best_subtitle += b

    if len(b) == 0:
        for i in range(len(a)):
            a[i].name = "from_eng"
        if parameter["comment_eng_sub"]:
            best_subtitle += [apply_sub(tg, "") for tg in a]
        else:
            best_subtitle += a

    if len(a) == 1 and len(b) == 1:
        best_subtitle += [apply_sub(a, b)]

    if len(a) == 1 and len(b) > 1:
        best_subtitle += combine_sub(a, b)

    if len(a) > 1 and len(b) == 1:
        best_subtitle += split_sub(a, b)

# translate = [re.findall(r"\{[^\{\}]+(\\N){0,1}[^\{\}]*\}[^\{\}]+(\\N){0,1}[^\{\}\\]*",ta.text) for ta in best_subtitle ]
translate = [re.findall(r"\{[^{}]+\\?N?[^{}]*}[^{}]+\\?N?[^{}\\]*", ta.text) for ta in best_subtitle]
translate = [item for row in translate for item in row]

for sign in sign_group:
    if not parameter["trans_sign"]:
        best_subtitle += [sign]
        continue
    temp = sign.plaintext.replace("\n", "\\N")
    tr = [ta for ta in translate if "{" + temp.replace(" ", "").lower() in ta.replace(" ", "").lower()]
    if len(tr) > 0:
        tr = tr[0]
        trans = tr[tr.index("}") + 1:]
        best_subtitle += [apply_sub(sign, trans)]
    else:
        best_subtitle += [sign]
# print(sign)

# Export
write_sub = pysubs2.load(parameter["origin_sub_path"])
while len(write_sub) > 0:
    del write_sub[0]

for b in best_subtitle:
    write_sub.append(b)

write_sub.save(parameter["output_filename"])

print("done")

window.close()
system("pause")






