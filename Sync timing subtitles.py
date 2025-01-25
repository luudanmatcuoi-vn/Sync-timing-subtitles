# Author       : Luudanmatcuoi
# yt link   : https://www.youtube.com/channel/UCdyAb9TAX1qQ5R2-c91-x8g
# GitHub link  : https://github.com/luudanmatcuoi-vn

import yaml, sys, pysubs2, re, argparse, requests, textdistance
from colour import Color
from os import system, remove
from os.path import isfile, join, splitext
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
sys.stdout.reconfigure(encoding='utf-8')

import PySimpleGUI as sg
import flet as ft
from flet_core.control_event import ControlEvent

try:
    req = requests.get("https://gist.github.com/luudanmatcuoi-vn/208833abf603e417efe1e6ccbb1be4f3")
    if "Allow" in req.text:
        pass
    else:
        print("Too old to work :v ")
        sys.exit()
except:
    print("Too old to work :v ")
    sys.exit()

with open("default.yaml", encoding="utf-8") as f:
    default_config = yaml.load(f, Loader=yaml.FullLoader)
with open("recent.yaml", encoding="utf-8") as f:
    recent_config = yaml.load(f, Loader=yaml.FullLoader)

def get_para_from_recent(default = False):
    if default:
        parameter = dict(default_config)
        parameter.pop('Dictionaries', None)
        parameter.pop('Tooltip', None)
    else:
        parameter = dict(recent_config)
    return parameter

def convert_parameter(controls={}, raw_data=False):
    global parameter, run_mode, list_characters
    if not raw_data:
        for ta in parameter.keys():
            if ta in controls.keys():
                parameter[ta] = controls[ta].value

    if parameter["framerate"] in [23.976023976023978,"23.976023976023978", 23.976, "23.976", 23.98, "23.98"]:
        parameter["framerate"] = 24000/1001
    parameter["framerate"] = float(parameter["framerate"])

    # Check output_filename
    pre, ext = splitext(parameter["output_filename"])
    parameter["output_filename"] = pre + ".ass"

    list_characters = parameter["characters"]
    
    # Save setting to recent if run_mode == window
    if run_mode:
        if type(parameter["color"]) == type([]):
            parameter["color"] = "__".join(parameter["color"])
        if type(parameter["ass_sign_tags"]) == type([]):
            parameter["ass_sign_tags"] = "__".join(parameter["ass_sign_tags"])

        recent_config = parameter
        with open("recent.yaml", "w", encoding="utf-8") as f:
            recent_config = yaml.dump( recent_config, stream=f, default_flow_style=False, sort_keys=False )

    if type(parameter["color"]) == type(""):
        parameter["color"] = parameter["color"].split("__")
    if type(parameter["ass_sign_tags"]) == type(""):
        parameter["ass_sign_tags"] = parameter["ass_sign_tags"].split("__")

    if isfile(parameter["origin_sub_path"]) and isfile(parameter["ocr_sub_path"]) and not parameter[
        "is_using_sushi"] or (isfile(parameter["origin_sub_path"]) and isfile(parameter["ocr_sub_path"]) and
                              isfile(parameter["origin_audio_path"]) and isfile(parameter["ocr_audio_path"])):
        return True, "Please wait..."
    else:
        return False, "Wrong path, please try again"

parameter = get_para_from_recent()

run_mode = True

# Define default values
parser = argparse.ArgumentParser()
for ta in parameter.keys():
    if ta in default_config["Tooltip"].keys():
        parser.add_argument('--'+ta , type=str, help=default_config["Tooltip"][ta])
    else:
        parser.add_argument('--'+ta , type=str)

args = parser.parse_args() # get arguments from command line
args = vars(args)
for g in args:
    if args[g] is not None:
        run_mode = False
        parameter[g] = args[g]

if not run_mode:
    _, _ = convert_parameter(raw_data=True)

class FileInputControl(ft.UserControl):
    def __init__(
        self,
        label: str = "",
        value: str = "",
        icon: str = "file",
        tooltip: str = "",
        disabled: bool = False,
        file_type: list = None,
    ):
        super().__init__()
        self.icon = icon
        self.text_value = value
        self.label = label
        self.tooltip = tooltip
        self.disabled = disabled
        self.file_type = ft.FilePickerFileType.CUSTOM if icon =="file" else ft.FilePickerFileType.ANY
        self.allowed_extensions = "ass;srt;ssa;vtt;sub;txt;tmp".split(";") if icon=="file" else []

    @property
    def value(self):
        return self.text_value

    @value.setter
    def value(self, e):
        self.text_value = e
        self.text_field.value = self.text_value
        self.text_field.update()

    def on_change(self, e):
        self.text_value = self.text_field.value

    def pick_files_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            selected_files = [file.path for file in e.files]
            self.text_field.value = selected_files[0]
            self.text_value = self.text_field.value
            self.text_field.update()
            
    def build(self):
        self.file_picker = ft.FilePicker( on_result=self.pick_files_result )
        
        self.pick_button = ft.IconButton(
            icon=ft.Icons.FILE_OPEN if self.icon == "file" else ft.Icons.VIDEO_FILE, disabled = self.disabled,
            on_click=lambda _: self.file_picker.pick_files( file_type=self.file_type, allowed_extensions = self.allowed_extensions )
        )

        self.text_field = ft.TextField(
            value=self.text_value, label=self.label,
            expand=True, border_width = 2, disabled = self.disabled, text_align=ft.TextAlign.RIGHT, on_change=self.on_change,
            tooltip = ft.Tooltip(message=default_config["Tooltip"][self.tooltip], padding=10, border_radius=5, text_style=ft.TextStyle(size=15, color=ft.Colors.SURFACE)),
            suffix= self.pick_button,
        )
        return ft.Stack( [ self.file_picker, self.text_field ] )

def main_window(page: ft.Page):
    page.title = 'Transfer timing subtitles by luudanmatcuoi v1.3.0'
    page.window.min_width = 800
    page.padding = 10
    page.window.icon = "dango.ico"
    page.size = 10
    page.scroll = "auto"

    def pick_files(e, file_type, control_to_update):
        file_picker = ft.FilePicker(
            on_result=lambda e: setattr(control_to_update, "value", e.files[0].path if e.files else "")
        )
        # page.overlay.append(file_pickera)
        file_picker.pick_files(
            allowed_extensions=[file_type] if file_type else None
        )

    def on_sushi_change(e):
        origin_audio_input.disabled = not e.control.value
        ocr_audio_input.disabled = not e.control.value
        page.update()

    def on_tag_change(e):
        if e.control.value:
            transfer_sign_cb.value = False
            transfer_sign_cb.disabled = True
        else:
            transfer_sign_cb.disabled = False
        page.update()

    def on_sign_change(e):
        if e.control.value:
            remove_tag_cb.value = False
            remove_tag_cb.disabled = True
        else:
            remove_tag_cb.disabled = False
        page.update()

    def reset_settings(e):
        parameter = get_para_from_recent(default = True)
        for key, value in parameter.items():
            if key in ["same_rate", "distance_string_rate", "distance_string_character"]:
                value = int(value*100)
            if key in controls:
                controls[key].value = value
        page.update()

    def changetheme(e):
        if page.theme_mode == "light":
            page.theme_mode = "dark"
            changetheme_btn.text = "Dark Mode"  # Change button text
        else:
            page.theme_mode = "light"
            changetheme_btn.text = "Light Mode"  # Change button text
        page.update()

    def on_submit(e):
        res, msg = convert_parameter(controls)
        if not res:
            if "try again" in logging_text.value:
                logging_text.value = logging_text.value + "."
            else:
                logging_text.value = msg
            page.update()
        else:
            page.window.close()

    def on_quit(e):
        global quit
        quit = True
        page.window.close()

    def slider_change(e,element):
        element.label = str(int(e.control.value)/100)
        page.update()

    def mk_tooltip(e):
        return ft.Tooltip(message=default_config["Tooltip"][e], padding=10, border_radius=5, text_style=ft.TextStyle(size=15, color=ft.Colors.SURFACE))

    # Rest of the controls    
    origin_sub_input = FileInputControl(label="Timed sub", value=parameter["origin_sub_path"], 
        icon = "file", tooltip="origin_sub_path" )
    origin_audio_input = FileInputControl(label="Audio/video", value=parameter["origin_audio_path"], 
        disabled=not parameter["is_using_sushi"], tooltip="origin_audio_path", icon = "audio" )
    ocr_sub_input = FileInputControl(label="OCR sub", value=parameter["ocr_sub_path"], 
        icon = "file", tooltip="ocr_sub_path" )
    ocr_audio_input = FileInputControl(label="Audio/video", value=parameter["ocr_audio_path"], 
        disabled= not parameter["is_using_sushi"], icon="audio" , tooltip="ocr_audio_path" )
    output_filename = ft.TextField(
        label="Output",
        value=parameter["output_filename"],
        expand=True,
        border_width=2,
    )
    sushi_cb = ft.Checkbox( label="Using sushi auto sync based on audio", 
        value=parameter["is_using_sushi"], on_change=on_sushi_change, tooltip=mk_tooltip("is_using_sushi") )
    spell_checker_cb = ft.Checkbox( label="Using spell checker", value=parameter["is_spell_checker"],
        tooltip=mk_tooltip("is_spell_checker") )
    comment_timed_cb = ft.Checkbox( label="Timed sub", value=parameter["comment_timed_sub"], 
        tooltip=mk_tooltip("comment_timed_sub") )
    comment_ocr_cb = ft.Checkbox( label="OCR sub", value=parameter["comment_ocr_sub"],
        tooltip=mk_tooltip("comment_ocr_sub") )
    remove_tag_cb = ft.Checkbox( label="Remove tags and signs in ocr sub", value=parameter["is_remove_tag"], 
        on_change=on_tag_change, tooltip=mk_tooltip("is_remove_tag") )
    transfer_sign_cb = ft.Checkbox( label="Using signs in ocr_sub", value=parameter["is_transfer_sign"], 
        on_change=on_sign_change, tooltip=mk_tooltip("is_transfer_sign") )
    same_rate = ft.Slider( on_change= lambda e:slider_change(e,same_rate), min=0, max=100, value=parameter["same_rate"], 
        divisions=100, expand=True, tooltip=mk_tooltip("same_rate") )
    distance_string_rate = ft.Slider( on_change= lambda e:slider_change(e,distance_string_rate), min=0, max=100, 
        value=parameter["distance_string_rate"], divisions=100, expand=True, tooltip=mk_tooltip("distance_string_rate"))
    distance_string_character = ft.Slider( on_change= lambda e:slider_change(e,distance_string_character), min=0, max=100, 
        value=parameter["distance_string_character"], divisions=100, expand=True, tooltip=mk_tooltip("distance_string_character") )
    framerate = ft.TextField( label="framerate", value=str(parameter["framerate"]), width=200, expand=True, 
        tooltip=mk_tooltip("framerate") )
    frame_distance = ft.Slider( label="{value}%", min=0, max=20, value=parameter["frame_distance"], 
        divisions=20, expand=True, tooltip=mk_tooltip("frame_distance") )
    frame_range = ft.Slider( label="{value}%", min=10, max=100000, value=parameter["frame_range"], 
        expand=True, tooltip=mk_tooltip("frame_range") )
    sample_shift_range = ft.Slider( label="{value}%", min=4, max=1000, value=parameter["sample_shift_range"], 
        expand=True, tooltip=mk_tooltip("sample_shift_range") )
    changetheme_btn = ft.Button("Light Mode" if page.theme_mode == "light" else "Dark Mode", on_click=changetheme)

    logging_text = ft.Text(value="")
    reset_btn = ft.ElevatedButton("Reset settings", on_click=reset_settings)
    submit_btn = ft.ElevatedButton("Ok", on_click=on_submit)
    quit_btn = ft.ElevatedButton("Quit", on_click=on_quit)
    empty = ft.Container(width=15)
    empty_ex = ft.Container(expand=True)

    controls = {
        "origin_sub_path": origin_sub_input,
        "ocr_sub_path": ocr_sub_input,
        "origin_audio_path": origin_audio_input,
        "ocr_audio_path": ocr_audio_input,
        "output_filename": output_filename,
        "is_using_sushi": sushi_cb,
        "is_spell_checker": spell_checker_cb,
        "comment_timed_sub": comment_timed_cb,
        "comment_ocr_sub": comment_ocr_cb,
        "is_remove_tag": remove_tag_cb,
        "is_transfer_sign": transfer_sign_cb,
        "same_rate": same_rate,
        "distance_string_rate": distance_string_rate,
        "distance_string_character": distance_string_character,
        "framerate": framerate,
        "frame_distance": frame_distance,
        "frame_range": frame_range,
        "sample_shift_range": sample_shift_range,
        "changetheme_btn": changetheme_btn,
    }

    content = ft.Container(
        content=ft.Column(
            [   ft. Container( content = ft.Row(
                    [ ft.Column(  # Left column
                        [ft.Text("Timed Files", size=16, weight=ft.FontWeight.BOLD),
                        origin_sub_input,
                        origin_audio_input,
                        ], expand=True, spacing=10,),
                    ft.Column(  # Right column
                        [ ft.Text("OCR Files", size=16, weight=ft.FontWeight.BOLD),
                          ocr_sub_input,
                          ocr_audio_input,
                        ], expand=True, spacing=10,),   ],
                    spacing=10, ), margin=ft.margin.only(bottom=20)
                ),
                output_filename,
                ft.Row([sushi_cb, spell_checker_cb, empty ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("Comment lines that only appear in: "), comment_timed_cb, comment_ocr_cb]),
                remove_tag_cb,
                transfer_sign_cb,
                ft.ExpansionTile(
                    title=ft.Text("Addition parameters", size=16, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text("Change it if subtitle not sync probably"),
                    affinity=ft.TileAffinity.PLATFORM,
                    trailing=ft.Icon(ft.Icons.ARROW_DROP_DOWN),
                    maintain_state=True,
                    controls=[
                            ft.Row([ft.Text("Same Rate :"), same_rate ]),
                            ft.Row([ft.Text("distance_string_rate :"), distance_string_rate ]),
                            ft.Row([ft.Text("distance_string_character :"), distance_string_character ]),
                            ft.Row([ft.Text("distance_string_character :"), frame_distance ]),
                            ft.Row([framerate, empty_ex ]),
                            ft.Row([ft.Text("For extend function:", size=16, weight=ft.FontWeight.BOLD), empty_ex ]),
                            ft.Row([ft.Text("frame_range :"), frame_range ]),
                            ft.Row([ft.Text("sample_shift_range :"), sample_shift_range ]),
                        ],
                ),
                logging_text,
                ft.Row(
                    [reset_btn, empty, changetheme_btn, empty_ex, submit_btn, empty, quit_btn, empty],
                    alignment=ft.MainAxisAlignment.SPACE_AROUND
                )
            ],
            spacing=2,
            scroll=ft.ScrollMode.AUTO
        ),
        padding=ft.padding.all(10),
        expand=True
    )

    page.add(content)

if run_mode:
    ft.app(target = main_window)
    if "quit" in globals():
        exit()

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

def normalized_time_data(group,listgroup):
    start = min([g["start"] for t in listgroup for g in t ])
    end = max([g["end"] for t in listgroup for g in t])
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

    max_level = max([g["level"] for g in graph])
    import flet.canvas as cvw
    cp = cvw.Canvas(
        [
            cvw.Rect( x = g["level"]*(20+10), y = g["start_nom"]-50, 
                width = 20, height = g["end_nom"]-g["start_nom"], paint=ft.Paint(g["color"])) for g in graph
        ], width = (max_level+1)*30
        )
    return cp

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

    def split_page(page: ft.Page):
        page.title = "Transfer timing subtitle"
        page.window.width = 1000
        page.window.height = 400
        page.window.resizable = True
        page.padding = 20

        text_width = 45
        a_group_list = [ ft.Row( controls = [ft.Container( content = ft.Text(a_group[t].text), padding = 10, expand=True,
                        border = ft.border.all(3, gen_color(t,lum=3/5) ) )] ) for t in range(len(a_group)) ] 
        
        b_group_list = [ ft.TextField( border_width = 3,
                        value=b_group[t]["text"], border_color = gen_color(t,lum=2/5,sat=2/3), 
                        multiline = True) for t in range(len(b_group)) ] 

        #Prepare for graphic visualize
        temp_graph = [[{"text":ga.text,"start":ga.start,"end":ga.end} for ga in a_group],b_group]
        graph1 = normalized_time_data([{"text":ga.text,"start":ga.start,"end":ga.end} for ga in a_group], temp_graph)
        graph2 = normalized_time_data(b_group, temp_graph)
        
        def handle_swap(e):
            if len(a_group_list) < 2:
                return
            values = [field.value for field in b_group_list]
            temp = values[0]
            for i in range(len(values) - 1):
                b_group_list[i].value = values[i + 1]
            b_group_list[-1].value = temp
            page.update()

        def handle_combine(e):
            if not b_group_list:
                return
            combined_text = " ".join(field.value for field in b_group_list if field.value)
            b_group_list[0].value = combined_text
            for field in b_group_list[1:]:
                field.value = ""
            page.update()

        def handle_duplicate(e):
            if not b_group_list:
                return
            first_value = b_group_list[0].value
            for field in b_group_list[1:]:
                field.value = first_value
            page.update()

        def handle_copy_timed(e):
            for i, (a_field, b_field) in enumerate(zip(a_group_list, b_group_list)):
                b_field.value = a_field.content.value
            page.update()

        def handle_ok(e):
            # Get values from fields
            a_group_values = [field.controls[0].content.value for field in a_group_list]
            b_group_values = [field.value for field in b_group_list]
            
            b_group_values = [ re.sub(r"\{[^\{\\\}]*\\[^\{\}]+\}", "", text.strip())
                                for text in b_group_values ]
            for i in range(len(a_group_values)):
                a_group[i] = apply_sub(a_group[i], b_group_values[i])
            page.window.close()

        def handle_quit_btn(e):
            parameter["quit_split_line_section"] = True
            for g in range(len(a_group)):
                a_group[g] = apply_sub(a_group[g], b_group[g])
            page.window.close()
            
        # Layout
        content = ft.Column( controls = [ft.Row(
                controls=[
                    ft.Column(
                        controls= [ ft.Text("Timed sub") ] + a_group_list,
                        scroll=ft.ScrollMode.AUTO, expand=True
                    ),
                    graph1,
                    ft.Container(width=5, height=120, bgcolor="white"),
                    graph2,
                    ft.Column(
                        controls= [ft.Text("OCR sub")] + b_group_list,
                        scroll=ft.ScrollMode.AUTO, expand=True
                    ),
                ], expand=True, alignment = ft.MainAxisAlignment.START
            )] , scroll=ft.ScrollMode.AUTO )

        log_txt = ft.Text("(Aegisub tags will be auto transferred)")
        swap_btn = ft.Button("Swap", on_click=handle_swap)
        combine_btn = ft.Button("Combine", on_click=handle_combine)
        dup_btn = ft.Button("Duplicate", on_click=handle_duplicate)
        copy_btn = ft.Button("Copy timed_sub", on_click=handle_copy_timed)
        ok_btn = ft.Button("Ok", on_click=handle_ok)
        cancel_btn = ft.Button("Cancel", on_click=lambda _: page.window.close())
        quit_btn = ft.Button("Quit section + Apply all", on_click=handle_quit_btn)
        con_ex = ft.Container(expand=True)
        con = ft.Container(width=15, height=10)

        real_content = ft.Container(
            content=ft.Column(
                [   content,
                    con,
                    ft.Row([log_txt,con_ex, swap_btn, con, combine_btn, con, dup_btn, con, copy_btn ], 
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, tight=50),
                    con,
                    ft.Row([ok_btn,cancel_btn,quit_btn], alignment=ft.MainAxisAlignment.END, spacing=10),
                ],
                spacing=2
            ),
            padding=ft.padding.all(10),
        )

        # Add everything to the page
        page.add( real_content)
    ft.app(target=split_page)

    return a_group

def check_spelling(stri):
    if len(stri) == 0:
        return [stri, True]
    suggestions = sym_spell.lookup(stri.lower(),Verbosity.CLOSEST,transfer_casing=False,max_edit_distance=2)
    try:
        result = suggestions[0]
    except:
        return [stri, False]
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
    #Load Dictionaries
    for dic_name in default_config["Dictionaries"]["name"].split("|"):
        dictionary_path = join("dictionaries", dic_name+".txt")
        for enc in default_config["Dictionaries"]["encode"].split("|"):
            try:
                sym_spell.load_dictionary(dictionary_path, 0, 1, encoding=enc)
                print("Loaded ",dic_name, " dictionary.")
                break
            except:
                pass
    #Load Bigram_Dictionaries
    for dic_name in default_config["Dictionaries"]["bigram_name"].split("|"):
        if dic_name=="": continue
        dictionary_path = join("dictionaries", dic_name+".txt")
        for enc in default_config["Dictionaries"]["encode"].split("|"):
            try:
                sym_spell.load_bigram_dictionary(dictionary_path, 0, 1, encoding=enc)
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
        sys.exit()

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
    if any(["\\" + tag + "(" in eng_sub[i_eng].text for tag in parameter["ass_sign_tags"] ]) and not eng_sub[
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

        # # Chia thành các mảng
        # temp = re.findall(
        #     r"|[^\s!\"#$%&\\\'()*+,\-./:;<=>?@\[\\\\\]^_`{|}~]+|[ \s!\"#$%&\\\'()*+,\-./:;<=>?@\[\\\\\]^_`{|}~]",
        #     ocr_sub[i_ocr].text.replace("\\N", "\n"))
        # print(temp)
        # for t in range(len(temp)):
        #     # Lọc các word có 1 ký tự
        #     tpattern = r'[a-zA-Z0-9\s!\"#$%&\'()*+,\-./:;<=>?@\[\]^_`\{\|\}\\~'+re.escape(list_characters)+r"]"
        #     if len(temp[t]) == 1 and re.search( tpattern , temp[t]):
        #         # Các word 1 ký tự là dấu câu hoặc số
        #         if re.search(
        #                 r"[\s()\"!,\'\-.;?_~a-zA-Z0-9%s]" % re.escape(list_characters),
        #                 temp[t]):
        #             temp[t] = [temp[t], True]
        #         else:
        #             temp[t] = [temp[t], False]
        #     else:
        #         sug = check_spelling(temp[t])
        #         temp[t] = sug

        # temp_res = len(temp) - sum([int(g[1]) for g in temp])
        # if temp_res > 0:
        #     line_need_correction += [[i_ocr, temp, ocr_sub[i_ocr].text]]

    from flask import Flask, render_template_string, request, jsonify
    app_spelling_check = Flask(__name__)
    HTML_TEMPLATE = """
    <!DOCTYPE html><html><head><title>Spelling Check</title><style>.container{max-width:800px;margin:20px auto;padding:20px}.text-area{width:100%;height:500px;margin:20px 0}.grey-text{color:#999}.red-text{color:red}.buttons{text-align:center;margin-top:20px}button{padding:10px 20px;margin:0 10px}#spelling{height:80vh;overflow-y:scroll}</style></head><body><div class="container"><h2 style="text-align:center">Double check pls...</h2><div id="spelling" class="text-area" , contenteditable="true">initial_text</div><div class="buttons"><button onclick="submitChanges()">Ok</button><button onclick="cancelChanges()">Cancel change</button></div></div><script>document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                window.close();
            }
        });
        function cancelChanges() {
            fetch('/cancel', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: "a"
            });
            window.close();
        }
        function submitChanges() {
            const textArea = document.getElementById('spelling');
            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    text: textArea.innerHTML
                })
            });
            alert("success, press okie to close webpage");
            window.close();
        }</script></body></html>"""

    import webbrowser, threading, sys
    from werkzeug.serving import run_simple
    class ServerThread(threading.Thread):
        def __init__(self, app):
            threading.Thread.__init__(self)
            self.srv = None  # Initialize server attribute
            self.app = app
            self.ctx = app.app_context()
            self.ctx.push()

        def run(self):
            self.srv = run_simple('127.0.0.1', 5000, self.app, use_debugger=False)
            self.srv.serve_forever()
            
        def shutdown(self):
            if self.srv:
                self.srv.shutdown()
                self.srv = None

    class ServerManager:
        def __init__(self):
            self.server = None

        def start_server(self):
            app = Flask('app_spelling_check')
            
            @app.route('/')
            def index_spelling_check():
                initial_text = []
                for lin in line_need_correction:
                    initial_text.append(f"[{lin[0]}]")
                    initial_text.append(f"<span class='grey-text' contenteditable = false>[{lin[2]}]</span>")
                    
                    spell_line = ''
                    for sp in lin[1]:
                        if sp[1]:  # if correct
                            spell_line += sp[0]
                        else:  # if incorrect
                            spell_line += f"<span class='red-text'>{sp[0]}</span>"
                    initial_text.append(spell_line)
                    initial_text.append('')  # Empty line for spacing
                return HTML_TEMPLATE.replace("initial_text", '<br>'.join(initial_text))

            @app.route('/submit', methods=['POST'])
            def submit_spelling_check():
                data = request.json
                data_spelling = data['text'].replace("\r", "")
                data_spelling = data_spelling.replace("<br>","\n")
                data_spelling = data_spelling.replace("</span>","")
                data_spelling = re.sub(r'<span class="[^\"]+"( contenteditable\=\"false\")*>',"", data_spelling)
                data_spelling = re.findall(r"\[([0-9]+)](\n\[[^]\[]+])?\n([^\[\]]+)", data_spelling + "\n\n")
                
                for da in data_spelling:
                    temp_da = [dq for dq in da if "[" not in dq and "]" not in dq and dq != "\n"]
                    if len(temp_da) == 0:
                        temp_da = ""
                    else:
                        temp_da = max(temp_da, key=len)
                    ocr_sub[int(da[0])].text = temp_da.lstrip().rstrip().replace("\n", "\\N")
                
                self.stop_server()
                return jsonify({"success": True})

            @app.route('/cancel', methods=['POST'])
            def cancel_spelling_check():
                self.stop_server()
                return jsonify({"success": True})

            self.server = ServerThread(app)
            self.server.start()

        def stop_server(self):
            if self.server:
                sys.exit()

    # Usage
    if __name__ == '__main__':
        manager = ServerManager()
        webbrowser.open('http://127.0.0.1:5000')
        manager.start_server()
        if manager.server:
            manager.server.join()

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
    return temp_group


if not parameter["is_transfer_sign"] and len(ocr_signs)>0:
    for sign in eng_signs:
        best_subtitle += [sign]
else:
    if len(eng_signs)>0:
        parameter["add_signs_timed_sub"] = True
        def popup_page(page: ft.Page):
            page.window.width = 350
            page.window.height = 200
            def close_dialog(response):
                parameter["add_signs_timed_sub"] = response
                page.window.close()

            page.add(
                ft.Column( controls = [
                    ft.Text("Do you want add signs from timed sub?\n(Signs will add as comment)"),
                    ft.Row( controls = [ ft.TextButton("Yes", on_click=lambda _: close_dialog(True) ),
                                             ft.TextButton("No", on_click=lambda _: close_dialog(False)),
                                        ], alignment=ft.MainAxisAlignment.CENTER ), ]) )

        ft.app(target=popup_page)

        if parameter["add_signs_timed_sub"]=="No" or parameter["add_signs_timed_sub"]==None:
            pass
        else:
            for sign in eng_signs:
                sign.type = "Comment"
                best_subtitle += [sign]

    # Find last id in best_subtitle
    last_best_subtitle_id = max([convert_actor(ga.name)["id"] for ga in best_subtitle])
    step_id = 2

    if len(ocr_signs)>0:
        parameter["shift_signs"] = sg.popup_yes_no("Shift signs from ocr_sub feature has to compare multi frames and it will take a while.\nMake sure you choose video source instead of audio.\nDo you want to shift signs ?")
        if parameter["shift_signs"]=="No" or parameter["shift_signs"]==None:
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

# window.close()
# system("pause")






