# Author       : Luudanmatcuoi
# yt link   : https://www.youtube.com/channel/UCdyAb9TAX1qQ5R2-c91-x8g
# GitHub link  : https://github.com/luudanmatcuoi-vn

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

# try:  
#     req = requests.get("https://anotepad.com/notes/ca7d4apf")
#     if "Allow" in req.text:
#         pass
#     else:
#         print("Too old to work :v ")
#         exit()
# except:
#     print("Too old to work :v ")
#     exit()


config = configparser.ConfigParser()
config.read('config.ini', encoding = "utf8")

# for key in config["Tooltip"]:
#     config["Tooltip"][key] = config["Tooltip"][key].replace("\\n","\n")

def get_para_from_recent(default = False):
    if default:
        parameter = dict(config["Default"])
    else:
        parameter = dict(config["Recent"])
    for k in parameter.keys():
        if parameter[k] == "True":
            parameter[k] = True
        elif parameter[k] == "False":
            parameter[k] = False
        elif parameter[k].replace(".","").isdigit():
            if ".0" in parameter[k] or "." not in parameter[k]:
                parameter[k] = int(float(parameter[k])//1)
            else:
                parameter[k] = float(parameter[k])
    return parameter
parameter = get_para_from_recent()

sym_spell = SymSpell()

for dic_name in config["Dictionaries"]["name"].split("|"):
    dictionary_path = join("dictionaries", dic_name+".txt")
    for enc in config["Dictionaries"]["encode"].split("|"):
        try:
            sym_spell.load_dictionary(dictionary_path, 0, 1, encoding=enc)
            break
        except:
            pass

# Define the window's contents ,tooltip = config["Tooltip"]["origin_sub_path"]
layout = [[sg.Text("Timed sub: ",tooltip = config["Tooltip"]["origin_sub_path"]), 
           sg.Input(key="origin_sub_path",tooltip = config["Tooltip"]["origin_sub_path"], change_submits=True, expand_x=True, default_text=parameter["origin_sub_path"]),
           sg.FileBrowse(key='origin_sub_path',file_types=(("Subtitles", "*.ass"),("Subtitles", "*.srt")))],
          [sg.Text("OCR sub: ",tooltip = config["Tooltip"]["ocr_sub_path"]),
           sg.Input(key="ocr_sub_path",tooltip = config["Tooltip"]["ocr_sub_path"], change_submits=True, expand_x=True, default_text=parameter["ocr_sub_path"]),
           sg.FileBrowse(key='ocr_sub_path',file_types=[("Subtitle files","*."+fo) for fo in ["ass","srt","ssa","vtt","sub","txt","tmp"] ])],
          
          [sg.Text("Audio/video of timed sub: ",tooltip = config["Tooltip"]["origin_audio_path"]), 
           sg.Input(key="origin_audio_path",tooltip = config["Tooltip"]["origin_audio_path"], change_submits=True, expand_x=True, default_text=parameter["origin_audio_path"]),
           sg.FileBrowse(key='origin_audio_path')],
          [sg.Text("Audio/video of ocr sub: ",tooltip = config["Tooltip"]["ocr_audio_path"]),
           sg.Input(key="ocr_audio_path",tooltip = config["Tooltip"]["ocr_audio_path"], change_submits=True, expand_x=True, default_text=parameter["ocr_audio_path"]),
           sg.FileBrowse(key='ocr_audio_path')],
          
          [sg.Text("Output: ",tooltip = config["Tooltip"]["output_filename"]),
           sg.Input(key="output_filename", expand_x=True, default_text=parameter["output_filename"])],


          [sg.Checkbox(text="Using sushi auto sync based on audio",tooltip = config["Tooltip"]["is_using_sushi"], key="is_using_sushi", enable_events=True, default=parameter["is_using_sushi"])],
          [sg.Checkbox(text="Using spell checker",tooltip = config["Tooltip"]["is_spell_checker"], key="is_spell_checker", default=parameter["is_spell_checker"])],
          
          [sg.Checkbox(text="Comment from_eng sub",tooltip = config["Tooltip"]["comment_eng_sub"], key="comment_eng_sub", default=parameter["comment_eng_sub"])],
          [sg.Checkbox(text="Comment from_ocr sub",tooltip = config["Tooltip"]["comment_ocr_sub"], key="comment_ocr_sub", default=parameter["comment_ocr_sub"])],
          
          [sg.Text("same_rate: ",tooltip= config["Tooltip"]["same_rate"]), 
           sg.Spin([ig / 100 for ig in range(101)], parameter["same_rate"], key="same_rate", size=(20, 1))],
          [sg.Text("distance_string_rate: ",tooltip=config["Tooltip"]["distance_string_rate"]),
           sg.Spin([ig / 100 for ig in range(101)], parameter["distance_string_rate"], key="distance_string_rate",size=(20, 1))],
          [sg.Text("distance_string_character: ",tooltip=config["Tooltip"]["distance_string_character"]),
           sg.Spin([ig for ig in range(10)], parameter["distance_string_character"], key="distance_string_character",size=(20, 1))],
          
          [sg.Text("framerate: ",tooltip = config["Tooltip"]["framerate"]), sg.Input(key="framerate", size=(20, 1), default_text=parameter["framerate"])],
          [sg.Text("frame_distance: ",tooltip = config["Tooltip"]["frame_distance"]),
           sg.Spin([ig for ig in range(10)], parameter["frame_distance"], key="frame_distance", size=(20, 1))],
          
          [sg.Text(size=(40, 1), key='log'),sg.Checkbox(text="quit_split_line_section",key="quit_split_line_section", default=False,visible=False),
           sg.Checkbox(text="Try translate sign", key="trans_sign", default=False, visible=False)],
          
          [sg.Button('Reset setting'), sg.Push(), sg.Button('Ok', size=(20, 1)), sg.Button('Quit')]]

# Create the window
window = sg.Window('Transfer timing subtitles by luudanmatcuoi v1.2.2', layout,icon='dango.ico')

# Display and interact with the Window using an Event Loop
while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Quit':
        exit()

    elif event == 'is_using_sushi':
        if values["is_using_sushi"]:
            window["origin_audio_path"].update(text_color='black',disabled=False)
            window["ocr_audio_path"].update(text_color='black',disabled=False)
        else:
            window["origin_audio_path"].update(text_color='grey60',disabled=True)
            window["ocr_audio_path"].update(text_color='grey60',disabled=True)

    if event == "Reset setting":
        parameter = get_para_from_recent(default = True)
        for ta in parameter.keys():
            try:
                values[ta]
                window[ta].update(parameter[ta])
            except:
                pass

    if event == "Ok":
        for ta in parameter.keys():
            if ta in values.keys():
                if values[ta] in ["True", "False", True, False]:
                    parameter[ta] = bool(values[ta])
                else:
                    try:
                        parameter[ta] = float(values[ta])
                    except:
                        if len(re.findall(r"[0-9]+/[0-9]+",values[ta]))>0:
                            parameter[ta] = int(values[ta].split("/")[0])/int(values[ta].split("/")[1])
                        else:
                            try:
                                parameter[ta] = str(values[ta])
                            except:
                                pass

        if parameter["framerate"] in [23.976023976023978, 23.976, 23.98]:
            parameter["framerate"] = 24000/1001
        # Check output_filename var
        pre, ext = splitext(parameter["output_filename"])
        parameter["output_filename"] = pre + ".ass"
        list_characters = parameter["characters"]

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
    # remove \N ở đầu câu
    temp_split_line = re.sub(r'^\\N {0,5}([a-z0-9' +re.escape(list_characters.lower())+r"])", r" \1", stri)
    temp_split_line = temp_split_line.replace("\\N", " ] ")
    # Tìm các mảng câu có dấu ngắt câu ở cuối
    temp_split_line = re.findall(
        r"[^!\"#$%&\\\'()*+,\-.\/:;<=>?@\[\\\]^_`{|}~]+|\.\.\.|[!\"#$%&\\\'()*+,\-.\/:;<=>?@\[\\\\\]^_`{|}~]+", temp_split_line)

    # Ngắt câu theo thứ tự ưu tiên
    result = ""
    for ch in ["]",".","!","?",";",",","-"]:
        if ch in temp_split_line and result=="":
            result = ["".join(temp_split_line[:temp_split_line.index(ch)+1]), \
                    "".join(temp_split_line[temp_split_line.index(ch)+1:])]
            try:
                result.remove("")
            except:
                pass
            if len(result)==1:
                result = ""
    if result == "":
        result = [stri]

    for ia in range(len(result)):
        # Xóa ]
        result[ia] = result[ia].replace("]", "").lstrip().rstrip()
        result[ia] = re.sub(r"^( ){0,3}[-\.]( ){0,3}","",result[ia])

        # Uppercase đầu câu
        if len(result[ia])>0:
            result[ia] = result[ia][0].upper() + result[ia][1:]

    try:
        result.remove("")
    except:
        pass

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
        a_group[0].name = a_group[0].name+"__tag:combine"

    return a_group


def split_sub(a_group, b_group):
    # Thử split sub theo các dấu trong câu
    def count_split_symbol(stri):
        return sum([stri.count(gt) for gt in parameter["punctuation"]])
    def split_line_dict(sow):
        sow = split_line(sow["text"])
        return [{"text":soww,"splited":True,"count":count_split_symbol(soww)} for soww in sow]

    split = [{"text":b_group[t].text,"splited":False,"count":count_split_symbol(b_group[t].text)} for t in range(len(b_group))]

    while len(split) < len(a_group):
        need_split = [s for s in split if not s["splited"]]
        if len(need_split)>0:
            need_split = max(need_split, key = lambda p : p["count"])
            need_split = split.index(need_split)
            split = split[:need_split] + split_line_dict(split[need_split]) + split[need_split+1:]
        else:
            break

    split = [s["text"] for s in split]

    b_group = split + [""] * ( len(a_group) - len(split) )

    # Gán tag:split vào a_group
    for q in range(len(a_group)):
        a_group[q].name = a_group[q].name+"__tag:split"

    if parameter["quit_split_line_section"]:
        for blablo in range(len(a_group)):
            a_group[blablo] = apply_sub(a_group[blablo], b_group[blablo])
        return a_group

    # Open window
    text_width = 45
    a_group_list = [[sg.Text("Timed sub")]] + [[sg.Multiline(key=f"a_group_{t}",
                                                              size=(text_width, len(a_group[t].text) // text_width + 2),
                                                              default_text=a_group[t].text, disabled=True)] for t in
                                                range(len(a_group))]
    b_group_list = [[sg.Text("OCR sub")]] + [[sg.Multiline(key=f"b_group_{t}",
                                                           size=(text_width, len(b_group[t]) // text_width + 2),
                                                           default_text=b_group[t])] for t in range(len(b_group))]
    split_layout = [[sg.Column(a_group_list), sg.VSeperator(), sg.Column(b_group_list), ],
                    [sg.Push(), sg.Button('Swap'), sg.Button('Combine'), sg.Button('Duplicate'),
                     sg.Button('Copy timed_sub')],
                    [sg.Push(), sg.Push(), sg.Push(), sg.Button('Ok'), sg.Button('Cancel'), sg.Push(), sg.Push(),
                     sg.Button('Quit section')]
                    ]
    split_window = sg.Window('Transfer timing subtitle by luudanmatcuoi', split_layout, finalize=True)
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
        if event == "Copy timed_sub":
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
            if any(ext in stri for ext in list_characters):
                result.term = result.term[0].upper() + result.term[1:]
                return [result.term, False]
            else:
                return [stri, True]
        else:
            return [result.term, False]

def convert_actor(va):
    if isinstance(va, str):
        res = {}
        va = va.split("__")
        for v in va:
            cla = v[v.index(":")+1:]
            try:
                cla = int(cla)
            except:
                pass
            res[v[:v.index(":")]] = cla
        return res
    elif isinstance(va, dict):
        res = []
        for d in va.keys():
            res+=[d+":"+str(va[d])]
        res = "__".join(res)
        return res


##########################################################################################
#### ----------------------------------------START ----------------------------------#####
##########################################################################################

### Sushi to sync sub by audio
if parameter["is_using_sushi"]:
    system(
        'sushi.exe --src "{ocr_audio_path}" --dst "{origin_audio_path}" --script "{ocr_sub_path}" -o ocr_sushi.'
        .format(  **parameter) + parameter["ocr_sub_path"][-3:])
    ocr_sub_sushi_path = "ocr_sushi."+ocr_sub_path[-3:]
else:
    ocr_sub_sushi_path = parameter["ocr_sub_path"]

# Load 2 file
eng_sub = pysubs2.load(parameter["origin_sub_path"])
ocr_sub = pysubs2.load(ocr_sub_sushi_path)

# Chèn object vào actor của eng_sub
for i_s in range(len(eng_sub)):
    old_name = eng_sub[i_s].name
    eng_sub[i_s].name = convert_actor( {"oldname":old_name, "id":str(i_s+1)} )

# Nhặt tất cả dialogue sign ra khỏi eng_sub
sign_group = []
i_eng = 0
while i_eng < len(eng_sub):
    if any(["\\" + tag + "(" in eng_sub[i_eng].text for tag in ["pos", "move", "org", "clip"]]) and not eng_sub[
        i_eng].is_comment:
        eng_sub[i_eng].name = eng_sub[i_eng].name+"__tag:sign"
        sign_group += [eng_sub[i_eng]]
        del eng_sub[i_eng]
    else:
        i_eng += 1

# Nhặt tất cả comment ra khỏi eng_sub
comment_group = []
i_eng = 0
while i_eng < len(eng_sub):
    if eng_sub[i_eng].is_comment:
        eng_sub[i_eng].name = eng_sub[i_eng].name+"__tag:comment"
        comment_group += [eng_sub[i_eng]]
        del eng_sub[i_eng]
    else:
        i_eng += 1

# Nhận diện layer thường sử dụng
layer_eng_sub = [eng.layer for eng in eng_sub if eng.layer!=0]
if len(layer_eng_sub)>0:
    layer_eng_sub = max(set(layer_eng_sub), key=layer_eng_sub.count)
else:
    layer_eng_sub = 0

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
            regex_str = r[2].replace("\\U","[UPPER]").replace("\\L","[LOWER]").replace("\\E","[END_UL]")
            ocr_sub[i_ocr].text = re.sub(r[1], regex_str, ocr_sub[i_ocr].text)
            if "[END_UL]" in ocr_sub[i_ocr].text:
                ocr_sub[i_ocr].text = re.sub(r"\[UPPER\]([^\[]*)\[END_UL\]", lambda m: f"{m.group(1).upper()}", ocr_sub[i_ocr].text)
                ocr_sub[i_ocr].text = re.sub(r"\[LOWER\]([^\[]*)\[END_UL\]", lambda m: f"{m.group(1).lower()}", ocr_sub[i_ocr].text)
    # Print cảnh báo các ký tự lạ
    match = re.findall(
        r"[^0-9a-zA-Z\s\W%s]" % list_characters,
        ocr_sub[i_ocr].text)
    if len(match) > 0 and "OCR_EMPTY_RESULT" not in ocr_sub[i_ocr].text:
        print("Caution unexpected characters:\t" + " ".join(match) + "\t" + ocr_sub[i_ocr].text)

    # Loại bỏ các line có 60-90% là các ký tự lạ
    tempa = ocr_sub[i_ocr].text.split("\\N")
    tempb = "dfasdfaergsergdzf".join(tempa).split("dfasdfaergsergdzf")
    for t in range(len(tempa)):
        tempa[t] = re.sub(  r"[^0-9a-zA-Z\s\W%s]" % re.escape(list_characters) , "", tempa[t])
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
if parameter["is_spell_checker"]:
    line_need_correction = []
    for i_ocr in range(len(ocr_sub)):
        # Chia thành các mảng
        temp = re.findall(
            r"|[^\s!\"#$%&\\\'()*+,\-./:;<=>?@\[\\\\\]^_`{|}~]+|[ \s!\"#$%&\\\'()*+,\-./:;<=>?@\[\\\\\]^_`{|}~]",
            ocr_sub[i_ocr].text.replace("\\N", "\n"))
        for t in range(len(temp)):
            # Lọc các word có 1 ký tự
            tpattern = r'[a-zA-Z0-9\s!\"#$%&\'()*+,\-./:;<=>?@\[\]^_`\{\|\}\\~'+re.escape(list_characters)+r"]"
            if len(temp[t]) == 1 and re.search( tpattern , temp[t]):
                # Các word 1 ký tự là dấu câu hoặc số
                if re.search(
                        r"[\s()\"!,\-.;?_~a-zA-Z0-9%s]" % re.escape(list_characters),
                        temp[t]):
                    temp[t] = [temp[t], True]
                else:
                    temp[t] = [temp[t], False]
            else:
                sug = check_spelling(temp[t])
                temp[t] = sug

        temp_res = len(temp) - sum([int(g[1]) for g in temp])
        if temp_res > 0:
            line_need_correction += [[i_ocr, temp, ocr_sub[i_ocr].text]]


    spelling_layout = [[sg.Push(), sg.Text('Double check pls...'), sg.Push()],
                       [sg.Multiline(key=f"spelling", size=(70, 20), default_text="")],
                       [sg.Push(), sg.Button('Ok'), sg.Button('Cancel change'), sg.Push()]]

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
        if event in (sg.WINDOW_CLOSED, "ESCAPE", "Cancel change"):
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
            spelling_window.close()
            break

i_ocr = 0
while i_ocr < len(ocr_sub):
    if ocr_sub[i_ocr] == "":
        del ocr_sub[i_ocr]
    else:
        i_ocr += 1






########################################## MAIN PART ######################################


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

# Link tất cả các sub với nhau -> lưu vào group
group = []
for ocr_line in ocr_sub:
    is_has_engsub_group = False
    for eng_line in eng_sub:
        same_time = cal_same_time(eng_line, ocr_line)
        if same_time > duration(eng_line)*parameter["same_rate"] or same_time > duration(ocr_line)*parameter["same_rate"]:
            group += [{"start": eng_line.start, "end": eng_line.end, "eng": eng_line, "ocr": ocr_line}]
            is_has_engsub_group = True
    if not is_has_engsub_group:
        group += [{"start": ocr_line.start, "end": ocr_line.end, "eng": None, "ocr": ocr_line}]

for eng_line in eng_sub:
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
        if group[temp_i]["ocr"] is None:
            break

        # Tìm kiếm sub chung -> đưa về a/b
        has_group_add = False
        for gia in range(len(a)):
            if group[temp_i]["eng"] == a[gia] and group[temp_i]["ocr"] != b[gia] and group[temp_i]["ocr"] is not None:
                a += [group[temp_i]["eng"]]
                b += [group[temp_i]["ocr"]]
                has_group_add = True
            elif (group[temp_i]["eng"] != a[gia] and group[temp_i]["ocr"] == b[gia] ) or \
                    is_same_time(group[i_group]["eng"],group[temp_i]["eng"]) :
                a += [group[temp_i]["eng"]]
                b += [group[temp_i]["ocr"]]
                has_group_add = True
        if not has_group_add:
            break

        following += 1

    def flat_line(l):
        return f"l_{str(l.layer)}_s_{str(l.start)}_e_{str(l.end)}_c_{str(l.is_comment)}_s_{str(l.style)}_n_{str(l.name)}_t_{str(l.text)}"

    g = 0
    while g<len(a):
        if flat_line(a[g]) in [flat_line(ka) for ka in a[:g]]:
            del a[g]
        else:
            g+=1
    g = 0
    while g<len(b):
        if flat_line(b[g]) in [flat_line(ka) for ka in b[:g]]:
            del b[g]
        else:
            g+=1

    i_group += following

    # Chia a và b vào các trường hợp
    if len(a) == 0:
        for i in range(len(b)):
            try:
                ids = convert_actor(best_subtitle[-1].name)["id"]
            except:
                ids = 0
            b[i].name = convert_actor({"tag":"from_ocr","oldname":"","id":ids})
            b[i].layer = layer_eng_sub
            b[i].type = "Comment"
        best_subtitle += b

    if len(b) == 0:
        for i_s in range(len(a)):
            a[i_s].name = a[i_s].name+"__tag:from_eng"
        if parameter["comment_eng_sub"]:
            best_subtitle += [apply_sub(tg, "") for tg in a]
        else:
            best_subtitle += a

    if len(a) == 1 and len(b) == 1:
        a[0].name = a[0].name+"__tag:"
        best_subtitle += [apply_sub(a, b)]

    if len(a) == 1 and len(b) > 1:
        best_subtitle += combine_sub(a, b)

    if len(a) > 1:
        best_subtitle += split_sub(a, b)

# Tìm các sub from_eng, from_sub cô độc đứng cạnh nhau
i_s = 0
while True:
    try:
        if "tag:from_" not in best_subtitle[i_s].name \
        and "tag:from_eng" in best_subtitle[i_s+1].name \
        and "tag:from_ocr" in best_subtitle[i_s+2].name \
        and "tag:from_" not in best_subtitle[i_s+3].name:
            best_subtitle[i_s+1] = apply_sub(best_subtitle[i_s+1], best_subtitle[i_s+2])
            best_subtitle[i_s+1].text = best_subtitle[i_s+1].text.replace("{[","{").replace("]}","}")
            best_subtitle[i_s+1].name = best_subtitle[i_s+1].name.replace("tag:from_eng","tag:")
            del best_subtitle[i_s+2]
        elif "tag:from_" not in best_subtitle[i_s].name \
        and "tag:from_ocr" in best_subtitle[i_s+1].name \
        and "tag:from_eng" in best_subtitle[i_s+2].name \
        and "tag:from_" not in best_subtitle[i_s+3].name:
            best_subtitle[i_s+2] = apply_sub(best_subtitle[i_s+2], best_subtitle[i_s+1])
            best_subtitle[i_s+2].text = best_subtitle[i_s+2].text.replace("{[","{").replace("]}","}")
            best_subtitle[i_s+2].name = best_subtitle[i_s+2].name.replace("tag:from_eng","tag:")
            del best_subtitle[i_s+1]
        else:
            i_s+=1
    except:
        break

# translate = [re.findall(r"\{[^\{\}]+(\\N){0,1}[^\{\}]*\}[^\{\}]+(\\N){0,1}[^\{\}\\]*",ta.text) for ta in best_subtitle ]
#translate = [re.findall(r"\{[^{}]+\\?N?[^{}]*}[^{}]+\\?N?[^{}\\]*", ta.text) for ta in best_subtitle]
#translate = [item for row in translate for item in row]
translate = []

for sign in sign_group:
    best_subtitle += [sign]

for comment in comment_group:
    best_subtitle += [comment]

#Sắp xếp best_subtitle theo đúng ids:
best_subtitle = sorted(best_subtitle, key= lambda tq: (convert_actor(tq.name)["id"], tq.start, tq.end ), reverse=False)

for sub in range(len(best_subtitle)):
    ob = convert_actor(best_subtitle[sub].name)
    ob = [str(ob["oldname"]), str(ob["tag"])]
    ob = [o for o in ob if o not in ["comment",""]]
    if len(ob)==2 and "sign" in ob:
        ob.remove("sign")
    ob = "-".join(ob)
    best_subtitle[sub].name = ob

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






