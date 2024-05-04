# Author       : Luudanmatcuoi
# yt link   : https://www.youtube.com/channel/UCdyAb9TAX1qQ5R2-c91-x8g
# GitHub link  : https://github.com/luudanmatcuoi-vn

import configparser
import pysubs2
import re
import requests
import textdistance
from colour import Color
from os import system, remove
from sys import exit
from os.path import isfile, join, splitext

import PySimpleGUI as sg

# try:
#     req = requests.get("https://gist.github.com/luudanmatcuoi-vn/208833abf603e417efe1e6ccbb1be4f3")
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

# Define the window's contents ,tooltip = config["Tooltip"]["origin_sub_path"]
layout = [[sg.Text("Timed sub: ",tooltip = config["Tooltip"]["origin_sub_path"]), 
           sg.Input(key="origin_sub_path",tooltip = config["Tooltip"]["origin_sub_path"], change_submits=True, expand_x=True, default_text=parameter["origin_sub_path"]),
           sg.FileBrowse(key='origin_sub_path',file_types=(("Subtitles", "*.ass"),("Subtitles", "*.srt")))],
          [sg.Text("OCR sub: ",tooltip = config["Tooltip"]["ocr_sub_path"]),
           sg.Input(key="ocr_sub_path",tooltip = config["Tooltip"]["ocr_sub_path"], change_submits=True, expand_x=True, default_text=parameter["ocr_sub_path"]),
           sg.FileBrowse(key='ocr_sub_path',file_types=[("Subtitle files","*."+fo) for fo in ["ass","srt","ssa","vtt","sub","txt","tmp"] ])],
          
          [sg.Text("Audio/video of timed sub: ",tooltip = config["Tooltip"]["origin_audio_path"]), 
           sg.Input(key="origin_audio_path",tooltip = config["Tooltip"]["origin_audio_path"], 
                change_submits=True, expand_x=True, default_text=parameter["origin_audio_path"],
                text_color= (lambda x: "black" if x else "grey60")(parameter["is_using_sushi"]),
                disabled = (lambda x: False if x else True ) (parameter["is_using_sushi"])),
           sg.FileBrowse(key='origin_audio_path')],
          [sg.Text("Audio/video of ocr sub: ",tooltip = config["Tooltip"]["ocr_audio_path"]),
           sg.Input(key="ocr_audio_path",tooltip = config["Tooltip"]["ocr_audio_path"], 
                change_submits=True, expand_x=True, default_text=parameter["ocr_audio_path"],
                text_color= (lambda x: "black" if x else "grey60")(parameter["is_using_sushi"]),
                disabled = (lambda x: False if x else True ) (parameter["is_using_sushi"])),
           sg.FileBrowse(key='ocr_audio_path')],
          
          [sg.Text("Output: ",tooltip = config["Tooltip"]["output_filename"]),
           sg.Input(key="output_filename", expand_x=True, default_text=parameter["output_filename"])],


          [sg.Checkbox(text="Using sushi auto sync based on audio",tooltip = config["Tooltip"]["is_using_sushi"], key="is_using_sushi", enable_events=True, default=parameter["is_using_sushi"])],
          [sg.Checkbox(text="Using spell checker",tooltip = config["Tooltip"]["is_spell_checker"], key="is_spell_checker", default=parameter["is_spell_checker"])],
          
          [sg.Checkbox(text="Comment from_timed sub",tooltip = config["Tooltip"]["comment_timed_sub"], key="comment_timed_sub", default=parameter["comment_timed_sub"])],
          [sg.Checkbox(text="Comment from_ocr sub",tooltip = config["Tooltip"]["comment_ocr_sub"], key="comment_ocr_sub", default=parameter["comment_ocr_sub"])],
          
          [sg.Checkbox(text="Remove tags and signs in ocr sub",tooltip = config["Tooltip"]["is_remove_tag"], 
                key="is_remove_tag", default=parameter["is_remove_tag"], enable_events = True,
                disabled = (lambda x: True if x else False ) (parameter["is_transfer_sign"]) )],
          [sg.Checkbox(text="Using signs in ocr_sub",tooltip = config["Tooltip"]["is_transfer_sign"], 
                key="is_transfer_sign", default=parameter["is_transfer_sign"], enable_events=True,
                disabled = (lambda x: True if x else False ) (parameter["is_remove_tag"]) )],
          
          [sg.Text("same_rate: ",tooltip= config["Tooltip"]["same_rate"]), 
           sg.Spin([ig / 100 for ig in range(101)], parameter["same_rate"], key="same_rate", size=(20, 1))],
          [sg.Text("distance_string_rate: ",tooltip=config["Tooltip"]["distance_string_rate"]),
           sg.Spin([ig / 100 for ig in range(101)], parameter["distance_string_rate"], key="distance_string_rate",size=(20, 1))],
          [sg.Text("distance_string_character: ",tooltip=config["Tooltip"]["distance_string_character"]),
           sg.Spin([ig for ig in range(10)], parameter["distance_string_character"], key="distance_string_character",size=(20, 1))],
          
          [sg.Text("framerate: ",tooltip = config["Tooltip"]["framerate"]), sg.Input(key="framerate", size=(20, 1), default_text=parameter["framerate"])],
          [sg.Text("frame_distance: ",tooltip = config["Tooltip"]["frame_distance"]),
           sg.Spin([ig for ig in range(10)], parameter["frame_distance"], key="frame_distance", size=(20, 1))],

          [sg.Text("For extend function",tooltip=config["Tooltip"]["extend_function"])],
          [sg.Text("frame_range: ",tooltip = config["Tooltip"]["frame_range"]),
           sg.Spin([ig for ig in range(10,100000)], parameter["frame_range"], key="frame_range", size=(20, 1))],
          [sg.Text("sample_shift_range: ",tooltip = config["Tooltip"]["sample_shift_range"]),
           sg.Spin([ig for ig in range(4,1000)], parameter["sample_shift_range"], key="sample_shift_range", size=(20, 1))],
        
          [sg.Checkbox(text="quit_split_line_section",key="quit_split_line_section", default=False,visible=False),
           sg.Checkbox(text="Try translate sign (signs from timed_ocr will add as comment)", key="trans_sign", default=False, visible=False)],
          
          [sg.Button('Reset setting'), sg.Push(), sg.Button('Ok', size=(20, 1)), sg.Button('Quit')]]

# Create the window
window = sg.Window('Transfer timing subtitles by luudanmatcuoi v1.2.4', layout,icon='dango.ico')

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
    
    elif event == 'is_remove_tag':
        if values["is_remove_tag"]:
            window["is_transfer_sign"].update(False,disabled=True)
        else:
            window["is_transfer_sign"].update(disabled=False)

    elif event == 'is_transfer_sign':
        if values["is_transfer_sign"]:
            window["is_remove_tag"].update(False,disabled=True)
        else:
            window["is_remove_tag"].update(disabled=False)

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

        # Check if output file output already exist
        if isfile(parameter["output_filename"]):
            double_check = sg.popup_yes_no("The '"+parameter["output_filename"].split("\\")[0]+"' file already exists. \nDo you want to overwrite it?",  title="Overwrite output file")
            if double_check=="No" or double_check==None:
                continue
            else:
                pass
        else:
            pass

        if parameter["framerate"] in [23.976023976023978, 23.976, 23.98]:
            parameter["framerate"] = 24000/1001

        # Check output_filename var
        pre, ext = splitext(parameter["output_filename"])
        parameter["output_filename"] = pre + ".ass"
        list_characters = parameter["characters"]

        if type(parameter["color"]) == type([]):
            parameter["color"] = "__".join(parameter["color"])

        # Save setting to recent
        config["Recent"] = parameter
        with open('config.ini', 'w', encoding = "utf8") as configfile:
            config.write(configfile)

        if type(parameter["color"]) == type(""):
            parameter["color"] = parameter["color"].split("__")

        if isfile(parameter["origin_sub_path"]) and isfile(parameter["ocr_sub_path"]) and not parameter[
            "is_using_sushi"] or (isfile(parameter["origin_sub_path"]) and isfile(parameter["ocr_sub_path"]) and
                                  isfile(parameter["origin_audio_path"]) and isfile(parameter["ocr_audio_path"])):
            print("Please wait...")
            break
        else:
            print("Wrong path, please try again")
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
    if line1 is None or line2 is None:
        return 0
    start1, end1 = line1.start, line1.end
    start2, end2 = line2.start, line2.end
    temp = (abs(start1 - end1) + abs(start2 - end2) - abs(start1 - start2) - abs(end1 - end2)) // 2
    if temp < 0:
        return 0
    else:
        return temp


def duration(line):
    if line is None:
        return 0
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


def is_continue_time(a, b ):
    if abs(a.end - b.start) < 1000 / parameter["framerate"] * parameter["frame_distance"]:
        return True
    else:
        False

def clean_inline_comment(stri):
    stri = stri.replace("\\N","[")
    stri = re.sub(r"\{[^\\\{\}]+\}","",stri)
    return stri.replace("[","\\N")

def flat_line(l):
    if l is None:
        return ""
    return f"l_{str(l.layer)}_s_{str(l.start)}_e_{str(l.end)}_c_{str(l.is_comment)}_s_{str(l.style)}_n_{str(l.name)}_t_{str(l.text)}"

def gen_color(stt, lum=None, sat = None):
    if type(stt)==type(1):
        c = Color(parameter["color"][stt%len(parameter["color"])])
    else:
        c = Color(stt)
    if lum!=None:
        c.luminance = lum
    if sat!=None:
        c.saturation = sat
    return c.hex_l

def normalized_time_data(group):
    start = min([g["start"] for g in group])
    end = max([g["end"] for g in group])
    le = abs(end-start)
    graph = group
    for g in range(len(graph)):
        graph[g]["start_nom"] = int((graph[g]["start"] - start)/le*100//1)
        graph[g]["end_nom"] = int((graph[g]["end"] - start)/le*100//1)
        graph[g]["color"] = gen_color(g)
        graph[g]["level"] = 0

    for g in range(len(graph)):
        while True:
            same_level = [graph[ga] for ga in range(g) if graph[ga]["level"] == graph[g]["level"]]
            if any([ ( abs(sa["start"]-sa["end"]) + abs(graph[g]["start"]-graph[g]["end"]) - 
                abs(sa["start"]-graph[g]["start"]) -abs(sa["end"]-graph[g]["end"]) ) > 2 for sa in same_level ]):
                graph[g]["level"] +=1
            else:
                break

    return graph


def apply_sub(a_line, text):
    # Change all type to a_line:ssa_line ; text:string
    if type(a_line) == type([]) and len(a_line) == 1:
        a_line = a_line[0]
    if type(text) == type({}):
        text = text["text"]
    elif type(text) != type("") and type(text) != type([]):
        text = text.text
    elif type(text) == type([]) and len(text) == 1:
        text = text[0].text
    # Handle \n \\N \\n
    text = text.replace("\n","\\N")
    text = text.replace("\\n","\\N")
    # throw all aegisub tag {} -> [] in a_line
    temp = re.sub(r"\{([^\\]+)}", r"[\1]", a_line.text)

    match = re.findall(r"(({[^{}]+})?([^{}]+)?({[^{}]+})?)+", temp)
    temp = ""
    for t in match:
        for m in t:
            if m == "":
                pass
            # If aegisub tag in match -> add to temp
            elif "{" in m:
                temp += m
            # If aegisub tag not in match (aka timed sub) -> comment it {} and add to temp
            elif "{" not in m:
                if parameter["apply_mode"] == "comment":
                    temp += "{" + m + "}"
                else:
                    pass
    text = temp + text
    #Remove duplicate comment
    text = re.sub(r"(\{[^\{\}]+\}({[^\{\}]+\})*)\1{1,}",r"\1",text)
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
    # If a_line got \\N -> combine with \\N. Else combine with space
    if "\\N" in a_group[0].text and len(b_group) > 1:
        def clear_newline(stri):
            stri = re.sub(r"( )*\n( )*"," ",stri)
            stri = re.sub(r"( )*\\N( )*"," ",stri)
            return stri
        b_group[0].text = "\\N".join([clear_newline(t.plaintext) for t in b_group])
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
        kwow = split_line(sow["text"])
        return [{"text":kwows,"splited":True,
                 "start": sow["start"], "end": sow["end"],
                 "count":count_split_symbol(kwows)} for kwows in kwow]

    split = [{"text":clean_inline_comment(b_group[t].text), "splited":False,
             "count":count_split_symbol(b_group[t].text),
             "start": b_group[t].start, 
             "end": b_group[t].end  } for t in range(len(b_group))]

    while len(split) < len(a_group):
        need_split = [s for s in split if not s["splited"]]
        if len(need_split)>0:
            need_split = max(need_split, key = lambda p : p["count"])
            need_split = split.index(need_split)
            split = split[:need_split] + split_line_dict(split[need_split]) + split[need_split+1:]
        else:
            break

    # split = [s["text"] for s in split]

    # Remove phrase in split that duplicate
    tempsplit = [t["text"].split("\\N") for t in split]
    for g in range(len(tempsplit)):
        for q in tempsplit[g]:
            if q in [bla for qa in tempsplit[:g] for bla in qa ] and len(tempsplit[g])>1:
                tempsplit[g].remove(q)
    tempsplit = ["\\N".join(t) for t in tempsplit]
    for g in range(len(tempsplit)):
        split[g]["text"] = tempsplit[g]
    try:
        b_group = split + [{"text":"", "splited":True, "count":0, "start": split[-1]["end"],  "end": split[-1]["end"]  }] * ( len(a_group) - len(split) )
    except:
        b_group = split + [{"text":"", "splited":True, "count":0, "start": 0,  "end": 1  }] * ( len(a_group) - len(split) )

    # Gán tag:split vào a_group
    for q in range(len(a_group)):
        a_group[q].name = a_group[q].name+"__tag:split"

    # Check is quit_split_line_section enable
    if parameter["quit_split_line_section"] and len(a_group) >= len(b_group):
        for blablo in range(len(a_group)):
            a_group[blablo] = apply_sub(a_group[blablo], b_group[blablo])
        return a_group

    #Prepare for graphic visualize
    graph1 = normalized_time_data([{"text":ga.text,"start":ga.start,"end":ga.end} for ga in a_group])
    max_graph_level_1 = max([ga["level"] for ga in graph1])
    graph2 = normalized_time_data(b_group)
    max_graph_level_2 = max([ga["level"] for ga in graph2])

    # Open window
    text_width = 45
    a_group_list = [[sg.Text("Timed sub")]] + [[sg.Multiline(key=f"a_group_{t}",
                                                  size=(text_width, len(a_group[t].text) // text_width + 2),
                                                  sbar_background_color = gen_color(t,lum=3/5),
                                                  default_text=a_group[t].text, disabled=True, autoscroll = False)] for t in
                                                range(len(a_group))]
    b_group_list = [[sg.Text("OCR sub")]] + [[sg.Multiline(key=f"b_group_{t}",
                                                  size=(text_width, len(b_group[t]) // text_width + 2),
                                                  sbar_background_color = gen_color(t,lum=2/5,sat=2/3),
                                                  default_text=b_group[t]["text"])] for t in range(len(b_group))]
    split_layout = [[sg.Column(a_group_list), 
                     sg.Graph(((max_graph_level_1+1)*7-3, 100), (0,0), ((max_graph_level_1+1)*7-3, 100), k='-GRAPH1-'),
                     sg.VSeperator(),
                     sg.Graph(((max_graph_level_2+1)*7-3, 100), (0,0), ((max_graph_level_2+1)*7-3, 100), k='-GRAPH2-'), 
                     sg.Column(b_group_list), ],
                    [sg.Text("(Aegisub tags will be auto transferred)"),sg.Push(), sg.Button('Swap'), sg.Button('Combine'), sg.Button('Duplicate'),
                     sg.Button('Copy timed_sub')],
                    [sg.Push(), sg.Push(), sg.Push(), sg.Button('Ok'), sg.Button('Cancel change'), sg.Push(),
                     sg.Button('Quit section + Apply all')]
                    ]
    split_window = sg.Window('Transfer timing subtitle by luudanmatcuoi', split_layout, finalize=True)
    split_window.bind("<Escape>", "ESCAPE")

    for ga in graph1:
        split_window['-GRAPH1-'].draw_rectangle((ga["level"]*7, 100-ga["start_nom"]), (ga["level"]*7+4, 100-ga["end_nom"]), fill_color=gen_color(ga["color"],lum=3/5), line_width=0)

    for ga in graph2:
        split_window['-GRAPH2-'].draw_rectangle((ga["level"]*7, 100-ga["start_nom"]), (ga["level"]*7+4, 100-ga["end_nom"]), fill_color=gen_color(ga["color"],lum=2/5,sat=2/3), line_width=0)

    while True:
        event, values = split_window.read()
        # See if user wants to quit or window was closed
        if event in (sg.WINDOW_CLOSED, "ESCAPE", "Cancel change"):
            split_window.close()
            return a_group
        if event == "Quit section + Apply all":
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
            # Get data from GUI
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
            # Remove all tags in b_group_result
            b_group_result = [re.sub(r"\{[^\{\\\}]*\\[^\{\}]+\}","",ga) for ga in b_group_result ]

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
                cla = float(cla)
                if cla%1 ==0:
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

############################################################################################
#### ------------------------------------- START ------------------------------------- #####
############################################################################################


if parameter["is_spell_checker"]:
    from symspellpy import SymSpell, Verbosity

    sym_spell = SymSpell()
    for dic_name in config["Dictionaries"]["name"].split("|"):
        dictionary_path = join("dictionaries", dic_name+".txt")
        for enc in config["Dictionaries"]["encode"].split("|"):
            try:
                sym_spell.load_dictionary(dictionary_path, 0, 1, encoding=enc)
                print("Loaded ",dic_name, " dictionary.")
                break
            except:
                pass

### Sushi to sync sub by audio
if parameter["is_using_sushi"]:
    ocr_sub_sushi_path = "ocr_sushi."+parameter["ocr_sub_path"][-3:]
    temp_check = system(
        'sushi.exe --src "{ocr_audio_path}" --dst "{origin_audio_path}" --script "{ocr_sub_path}" -o ocr_sushi.'
        .format(  **parameter) + parameter["ocr_sub_path"][-3:])
    if temp_check != 0:
        print("Some error from sushi.exe. \n  - Please put the 'sushi.exe' in the same location as .EXE file\n  - Make sure ffmpeg is installed.")
        system("pause")
        exit()

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
eng_signs = []
i_eng = 0
while i_eng < len(eng_sub):
    if any(["\\" + tag + "(" in eng_sub[i_eng].text for tag in ["pos", "move", "org", "clip"]]) and not eng_sub[
        i_eng].is_comment:
        eng_sub[i_eng].name = eng_sub[i_eng].name+"__tag:sign"
        eng_signs += [eng_sub[i_eng]]
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

# Detect most layer using
layer_eng_sub = [eng.layer for eng in eng_sub if eng.layer!=0]
if len(layer_eng_sub)>0:
    layer_eng_sub = max(set(layer_eng_sub), key=layer_eng_sub.count)
else:
    layer_eng_sub = 0

# Filter sub ocr : Remove empty lines, filter rules (find and replace), Caution unexpected characters
f = open('filter_rules.txt', "r", encoding="utf8")
rules = [g.replace("\\n", "\\\\N") for g in f.read().split("\n") if len(g) > 0]
rules = [g.split("________") for g in rules if "#" not in g[0]]
f.close()

# Check if characters parameter in config.ini is right
tempa = "".join([t.text for t in ocr_sub ]).replace(" ","").replace("\\N","").replace("\n","")
tempb = tempa
tempa = re.sub(  r"[^0-9a-zA-Z\s\W%s]" % re.escape(list_characters) , "", tempa)
if len(tempa) < len(tempb) * (1 - 20 / 100):
    print("Please fill all characters of your language in 'characters' config.ini\n(without A-Z a-z 0-9 or punctuation)")
    is_remove_lines_unexpected = False
else:
    is_remove_lines_unexpected = True

i_ocr = 0
ocr_signs = []
while i_ocr < len(ocr_sub):
    if ocr_sub[i_ocr].is_comment:
        del ocr_sub[i_ocr]
    # Remove tags in ocr_sub
    if parameter["is_remove_tag"]:
        if any(["\\" + tag + "(" in ocr_sub[i_ocr].text for tag in ["pos", "move", "org", "clip"]]):
            ocr_signs += [ocr_sub[i_ocr]]
            del ocr_sub[i_ocr]
            continue
        ocr_sub[i_ocr].text = re.sub(r"\{[^\{\\\}]*\\[^\{\}]+\}","",ocr_sub[i_ocr].text)
    else:
        if any(["\\" + tag + "(" in ocr_sub[i_ocr].text for tag in ["pos", "move", "org", "clip"]]):
            ocr_signs += [ocr_sub[i_ocr]]
            del ocr_sub[i_ocr]
            continue

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

    # Print Caution unexpected characters
    match = re.findall(
        r"[^0-9a-zA-Z\s\W%s]" % list_characters,
        ocr_sub[i_ocr].text)
    if len(match) > 0 and "OCR_EMPTY_RESULT" not in ocr_sub[i_ocr].text and is_remove_lines_unexpected :
        print("Caution unexpected characters:\t" + " ".join(match) + "\t" + ocr_sub[i_ocr].text)

    # Remove lines got 60-90% unexpected characters. or line is_comment
    tempa = ocr_sub[i_ocr].text.split("\\N")
    tempb = "dfasdfaergsergdzf".join(tempa).split("dfasdfaergsergdzf")
    for t in range(len(tempa)):
        tempa[t] = re.sub(  r"[^0-9a-zA-Z\s\W%s]" % re.escape(list_characters) , "", tempa[t])
        ga = tempa[t].replace(" ", "")
        gb = tempb[t].replace(" ", "")
        if len(ga) < len(gb) * (1 - 60 / 100) and is_remove_lines_unexpected:
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

###Block detect and fix spell checker
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
                        r"[\s()\"!,\'\-.;?_~a-zA-Z0-9%s]" % re.escape(list_characters),
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






########################################## MAIN PART ##########################################


# Change time stamp
temp_eng_time = [t.copy() for t in eng_sub if t.is_comment is False]
temp_eng_time = sorted(temp_eng_time, key=lambda t: t.start)
for i in range(len(ocr_sub)):
    for t in range(len(temp_eng_time) - 1):
        if cal_same_time(temp_eng_time[t + 1], ocr_sub[i]) ==0:
            continue
        if is_continue_time(temp_eng_time[t], temp_eng_time[t + 1]) \
                and ocr_sub[i].start < temp_eng_time[t].end < ocr_sub[i].end \
                and 1 - abs(
            1 - cal_same_time(temp_eng_time[t], ocr_sub[i]) / cal_same_time(temp_eng_time[t + 1], ocr_sub[i])) > \
                parameter["soft_combine_rate"]:
            if ocr_sub[i].start > temp_eng_time[t].start:
                ocr_sub[i].start = temp_eng_time[t].start
            if ocr_sub[i].end < temp_eng_time[t + 1].end:
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
    # if group[i_group]["eng"] is not None:
    a += [group[i_group]["eng"]]

    # if group[i_group]["ocr"] is not None:
    b += [group[i_group]["ocr"]]

    # Check Following group xem có trùng engline hay ocr line không ?
    following = 1
    real_following = 1
    while True:
        temp_i = i_group + following

        if temp_i == len(group):
            break

        is_group_add = False
        for gia in range(len(a)):
            if flat_line(group[temp_i]["eng"]) == flat_line(a[gia]) and flat_line(group[temp_i]["ocr"]) != flat_line(b[gia]):
                is_group_add = True

            if flat_line(group[temp_i]["eng"]) != flat_line(a[gia]) and flat_line(group[temp_i]["ocr"]) == flat_line(b[gia]) :
                is_group_add = True

            if is_same_time(a[gia],group[temp_i]["eng"]):
                is_group_add = True

            if is_same_time(b[gia],group[temp_i]["ocr"]):
                is_group_add = True

            if is_same_time(group[i_group]["eng"],group[temp_i]["eng"]):
                is_group_add = True

            if cal_same_time(group[temp_i]["ocr"],b[gia]) > duration(group[temp_i]["ocr"])*parameter["same_rate"]:
                is_group_add = True

            if cal_same_time(group[temp_i]["ocr"],b[gia]) > duration(b[gia])*parameter["same_rate"]:
                is_group_add = True
        if is_group_add:
            a += [group[temp_i]["eng"]]
            b += [group[temp_i]["ocr"]]
            real_following = following +1
        else:
            break

        following += 1

    # Remove duplicate elements in a and b group
    g = 0
    while g<len(a):
        if a[g] is None:
            del a[g]
        elif flat_line(a[g]) in [flat_line(ka) for ka in a[:g]]:
            del a[g]
        else:
            g+=1
    g = 0
    while g<len(b):
        if b[g] is None:
            del b[g]
        elif flat_line(b[g]) in [flat_line(ka) for ka in b[:g]]:
            del b[g]
        else:
            g+=1

    i_group += real_following

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

    elif len(b) == 0:
        for i_s in range(len(a)):
            a[i_s].name = a[i_s].name+"__tag:from_timed"
        if parameter["comment_timed_sub"]:
            best_subtitle += [apply_sub(tg, "") for tg in a]
        else:
            best_subtitle += a

    elif len(a) == 1 and len(b) == 1:
        a[0].name = a[0].name+"__tag:"
        best_subtitle += [apply_sub(a, b)]

    elif len(a) == 1 and len(b) > 1:
        best_subtitle += combine_sub(a, b)

    elif len(a) > 1:
        best_subtitle += split_sub(a, b)

# Tìm các sub from_eng, from_sub cô độc đứng cạnh nhau
i_s = 0
while True:
    try:
        if "tag:from_" not in best_subtitle[i_s].name \
        and "tag:from_timed" in best_subtitle[i_s+1].name \
        and "tag:from_ocr" in best_subtitle[i_s+2].name \
        and "tag:from_" not in best_subtitle[i_s+3].name:
            best_subtitle[i_s+1] = apply_sub(best_subtitle[i_s+1], best_subtitle[i_s+2])
            best_subtitle[i_s+1].text = best_subtitle[i_s+1].text.replace("{[","{").replace("]}","}")
            best_subtitle[i_s+1].name = best_subtitle[i_s+1].name.replace("tag:from_timed","tag:")
            del best_subtitle[i_s+2]
        elif "tag:from_" not in best_subtitle[i_s].name \
        and "tag:from_ocr" in best_subtitle[i_s+1].name \
        and "tag:from_timed" in best_subtitle[i_s+2].name \
        and "tag:from_" not in best_subtitle[i_s+3].name:
            best_subtitle[i_s+2] = apply_sub(best_subtitle[i_s+2], best_subtitle[i_s+1])
            best_subtitle[i_s+2].text = best_subtitle[i_s+2].text.replace("{[","{").replace("]}","}")
            best_subtitle[i_s+2].name = best_subtitle[i_s+2].name.replace("tag:from_timed","tag:")
            del best_subtitle[i_s+1]
        else:
            i_s+=1
    except:
        break

translate = []

### Transfer signs
def grouping_signs(group):
    temp_group = []
    gr = []
    for g in group:
        is_group_sign_add = False
        for r in gr:
            g_text = re.sub(r"\{.+}","",g.text)
            r_text = re.sub(r"\{.+}","",r.text)
            if is_same_time(g,r) or is_continue_time(g,r) or is_continue_time(r,g) or is_same_sub(g.text,r.text) :
                is_group_sign_add = True
        if is_group_sign_add or len(gr)==0:
            gr += [g]
        elif len(gr)>0:
            start = min([af.start for af in gr])
            end = max([af.end for af in gr])
            line = pysubs2.SSAEvent(start=start , end=end , text = str(len(temp_group)).zfill(4))
            temp_group += [{ "id":len(temp_group), "start":start, "end":end, "line":line, "group":gr}]
            gr = [g]
    if len(gr)>0:
        start = min([af.start for af in gr])
        end = max([af.end for af in gr])
        line = pysubs2.SSAEvent(start=start , end=end , text = str(len(temp_group)).zfill(4))
        temp_group += [{ "id":len(temp_group), "start":start, "end":end, "line":line, "group":gr}]
        gr = []
    # temp_i = 0
    # while True:
    #     ahaha = False
    #     for i in range(temp_i+1,len(temp_group)):
    #         temp_same_time = cal_same_time(temp_group[temp_i]["line"],temp_group[i]["line"])
    #         if same_time > duration(temp_group[temp_i]["line"])*parameter["same_rate"] or \
    #         same_time > duration(temp_group[i]["line"])*parameter["same_rate"] or \
    #         is_continue_time(temp_group[temp_i]["line"],temp_group[i]["line"]):
    #             temp_group[temp_i]["group"]+=temp_group[i]["group"]
    #             print(temp_i)
    #             del temp_group[i]
    #             ahaha = True
    #             break
    #     if not ahaha:
    #         temp_i+=1
    #     if temp_i == len(temp_group):
    #         break
    return temp_group


if not parameter["is_transfer_sign"] and len(ocr_signs)>0:
    for sign in eng_signs:
        best_subtitle += [sign]
else:
    if len(eng_signs)>0:
        add_signs_timed_sub = sg.popup_yes_no("Do you want add signs from timed sub?\n(Signs will add as comment)")
        if add_signs_timed_sub=="No" or add_signs_timed_sub==None:
            pass
        else:
            for sign in eng_signs:
                sign.type = "Comment"
                best_subtitle += [sign]

    # Find last id in best_subtitle
    last_best_subtitle_id = max([convert_actor(ga.name)["id"] for ga in best_subtitle])
    step_id = 2

    if len(ocr_signs)>0:
        shift_signs = sg.popup_yes_no("Shift signs from ocr_sub feature has to compare multi frames and it will take a while.\nMake sure you choose video source instead of audio.\nDo you want to shift signs ?")
        if shift_signs=="No" or shift_signs==None:
            # Add ocr_signs
            for ocr_sign in ocr_signs:
                ac = {"id":last_best_subtitle_id+step_id/10000, "tag":"sign","oldname":str(ocr_sign.name)}
                step_id+=1
                ocr_sign.name=convert_actor(ac)
                best_subtitle+=[ocr_sign]
        else:
            from skimage.metrics import structural_similarity
            import cv2
            import numpy as np
            from tqdm import tqdm

            def process_img(image1, image2):
                image11 = cv2.resize(image1, (256,144))
                image12 = cv2.resize(image2, (256,144))
                image1_gray = cv2.cvtColor(image11, cv2.COLOR_BGR2GRAY)
                image2_gray = cv2.cvtColor(image12, cv2.COLOR_BGR2GRAY)

                # Compute SSIM between the two images, score is between 0 and 1, diff is actuall diff with all floats
                (score, diff) = structural_similarity(image1_gray, image2_gray, full=True)
                return score

            vidcap1 = cv2.VideoCapture(parameter["origin_audio_path"])
            vidcap2 = cv2.VideoCapture(parameter["ocr_audio_path"])
            fps1 = vidcap1.get(cv2.CAP_PROP_FPS)
            fps2 = vidcap2.get(cv2.CAP_PROP_FPS)
            print("fps of 2 videos: ",fps1,fps2)

            ocr_sub_or = pysubs2.load(parameter["ocr_sub_path"])

            ocr_signs = []
            for i_ocr in range(len(ocr_sub_or)):
                if any(["\\" + tag + "(" in ocr_sub_or[i_ocr].text for tag in ["pos", "move", "org", "clip"]]):
                    ocr_signs += [ocr_sub_or[i_ocr]]
            ocr_signs = grouping_signs(ocr_signs)
            for ocr_sign in ocr_signs:
                frame_range = int(parameter["frame_range"])
                sample_shift_range = int(parameter["sample_shift_range"])

                #Video1
                start_shift_time = ocr_sign["line"].start - (sample_shift_range//2)/fps2*1000
                if start_shift_time<0:
                    vidcap2.set( cv2.CAP_PROP_POS_MSEC , 0 )
                else:
                    vidcap2.set( cv2.CAP_PROP_POS_MSEC , start_shift_time )
                ocr_images = []
                while True:
                    for i in range(sample_shift_range):
                        if  start_shift_time + i/fps2*1000 +1  < 0:
                            image = np.zeros((256, 144, 3), dtype = np.uint8)
                        else:
                            success,image = vidcap2.read()
                            if not success:
                                image = np.zeros((256, 144, 3), dtype = np.uint8)
                            else:
                               pass
                        ocr_images += [image]

                    if process_img(ocr_images[0], ocr_images[-1]) > 0.8:
                        if process_img(ocr_images[1], ocr_images[-1]) > 0.8:
                            sample_shift_range += 4
                            print("Sample images are too similar, extend sample_shift_range to ",sample_shift_range)
                    else:
                        break

                # Show ocr_images for debug only
                # for i in range(len(ocr_images)):
                #     if i ==0:
                #         vis = cv2.resize(ocr_images[i], (144,256)) 
                #     else:
                #         vis = np.concatenate((vis, cv2.resize(ocr_images[i], (144,256)) ), axis=1)
                # vis = cv2.resize(vis, dsize=(int(sample_shift_range*256+1), 144), interpolation=cv2.INTER_CUBIC)
                # cv2.imshow("a",vis)
                # cv2.waitKey(0) 

                #Video1
                while True:
                    start_set_video1 = start_shift_time - frame_range/fps1*1000
                    if start_set_video1<0:
                        vidcap1.set( cv2.CAP_PROP_POS_MSEC  , 0 )
                    else:
                        vidcap1.set( cv2.CAP_PROP_POS_MSEC  , start_set_video1 )
                    database_score = [[] for i in range(sample_shift_range)]
                    for frame_number in tqdm(range(0-frame_range,frame_range)):
                        # print(vidcap1.get(cv2.CAP_PROP_POS_MSEC) )
                        if  start_shift_time + (0+frame_number)/fps1*1000 +1 < 0:
                            image1 = np.zeros((256, 144, 3), dtype = np.uint8)
                        else:
                            success,image1 = vidcap1.read()
                            if not success:
                                image1 = np.zeros((256, 144, 3), dtype = np.uint8)
                            else:
                               pass
                        for i in range(len(database_score)):
                            database_score[i] += [process_img(image1, ocr_images[i])]

                    compare_database = [sum([ database_score[t][g+t] for t in range(sample_shift_range)]) for g in range(len(database_score[0])-sample_shift_range)]
                    temp_compare_database = max(compare_database)
                    if temp_compare_database < sample_shift_range* 0.8:
                        frame_range += 50
                        print("Result are sus, extend frame_range to ",frame_range)
                        continue
                    else:
                        compare_database = compare_database.index(temp_compare_database) - frame_range
                    print("Shift group '", re.sub(r"\{.+\}","", ocr_sign["group"][0].text ) , "' " ,compare_database, "frames")
                    break

                #Shift time, change actor name
                for ocr_sign_el in ocr_sign["group"]:
                    ac = {"id":last_best_subtitle_id+step_id/10000, "tag":"sign","oldname":str(ocr_sign_el.name)}
                    step_id+=1
                    ocr_sign_el.name=convert_actor(ac)
                    ocr_sign_el.shift(frames=compare_database,fps=fps1)
                    best_subtitle+=[ocr_sign_el]



for comment in comment_group:
    best_subtitle += [comment]

#Sord best_subtitle follow ids (remain order after do xyz stuff): 
best_subtitle = sorted(best_subtitle, key= lambda tq: (convert_actor(tq.name)["id"], tq.start, tq.end ), reverse=False)

for sub in range(len(best_subtitle)):
    ob = convert_actor(best_subtitle[sub].name)

    # Find marker line -> try to recover origin
    if re.match(r"^\{[^\{\}\\]+\}$",best_subtitle[sub].text) is not None:
        ob = [str(ob["oldname"])]
        best_subtitle[sub].text = best_subtitle[sub].text.replace("{[","{").replace("]}","}")
    else:
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

# Transfer styles
if parameter["ocr_sub_path"][-3:] in ["ass", "ssa"]:
    style_file = pysubs2.load(parameter["ocr_sub_path"])
    write_sub.import_styles(style_file)

for b in best_subtitle:
    write_sub.append(b)

write_sub.save(parameter["output_filename"])

print("DONE :v")

window.close()
system("pause")






