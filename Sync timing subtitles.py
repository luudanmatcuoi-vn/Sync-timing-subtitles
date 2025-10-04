# Author       : Luudanmatcuoi
# yt link   : https://www.youtube.com/channel/UCdyAb9TAX1qQ5R2-c91-x8g
# GitHub link  : https://github.com/luudanmatcuoi-vn

import re, argparse, requests, os, json, sys
import sushi, yaml, pysubs2, textdistance, imagehash
from colour import Color
from sys import exit
import flet as ft
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash
import signal, threading, time
from pyvi import ViTokenizer

try:
    req = requests.get("https://gist.github.com/luudanmatcuoi-vn/208833abf603e417efe1e6ccbb1be4f3")
    if "ALLOW2.0.0" in req.text:
        pass
    else:
        input("Too old to work :v Pls update...")
        exit()
except:
    print("Connect internet pls :3")
    exit()

root_folder = Path(__file__).parent.resolve()

with open(os.path.join(root_folder, "default.yaml" ), encoding="utf-8") as f:
    default_config = yaml.load(f, Loader=yaml.FullLoader)
with open(os.path.join(root_folder, "recent.yaml" ), encoding="utf-8") as f:
    recent_config = yaml.load(f, Loader=yaml.FullLoader)

def pysubs2load(str):
    try: 
        return pysubs2.load(str)
    except:
        return pysubs2.load(str, encoding="utf-16")

def get_para_from_recent(default = False):
    if default:
        parameter = dict(default_config)
        parameter.pop('Tooltip', None)
    else:
        parameter = dict(default_config)
        parameter.pop('Tooltip', None)
        temp_para = dict(recent_config)
        for k in parameter.keys():
            if k in temp_para.keys():
                parameter[k] = temp_para[k]
    return parameter

def convert_parameter(controls={}, raw_data=False):
    global parameter, run_mode, list_characters
    if not raw_data:
        for ta in parameter.keys():
            if ta in controls.keys():
                parameter[ta] = controls[ta].value

    default_par = dict(default_config)
    default_par.pop('Tooltip', None)
    for ta in parameter.keys():
        parameter[ta] = type(default_par[ta])(parameter[ta])

    if parameter["framerate"] in [23.976023976023978,"23.976023976023978", 23.976, "23.976", 23.98, "23.98"]:
        parameter["framerate"] = 24000/1001
    parameter["framerate"] = float(parameter["framerate"])
    parameter["is_using_sushi"] = bool(parameter["is_using_sushi"])
    parameter["custom_shift"] = float(parameter["custom_shift"])

    # Check output_filename
    pre, ext = os.path.splitext(parameter["output_filename"])
    parameter["output_filename"] = pre + ".ass"

    list_characters = parameter["characters"]
    
    # Save setting to recent if run_mode == window
    if run_mode:
        if type(parameter["color"]) == type([]):
            parameter["color"] = "__".join(parameter["color"])
        if type(parameter["ass_sign_tags"]) == type([]):
            parameter["ass_sign_tags"] = "__".join(parameter["ass_sign_tags"])

        recent_config = parameter
        with open(os.path.join(root_folder, "recent.yaml" ), "w", encoding="utf-8") as f:
            recent_config = yaml.dump( recent_config, stream=f, default_flow_style=False, sort_keys=False )

    if type(parameter["color"]) == type(""):
        parameter["color"] = parameter["color"].split("__")
    if type(parameter["ass_sign_tags"]) == type(""):
        parameter["ass_sign_tags"] = parameter["ass_sign_tags"].split("__")

    if os.path.isfile(parameter["origin_sub_path"]) and os.path.isfile(parameter["ocr_sub_path"]) and not parameter[
        "is_using_sushi"] or (os.path.isfile(parameter["origin_sub_path"]) and os.path.isfile(parameter["ocr_sub_path"]) and
                              os.path.isfile(parameter["origin_audio_path"]) and os.path.isfile(parameter["ocr_audio_path"])):
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

args, _  = parser.parse_known_args()
args = vars(args)
for g in args:
    if args[g] is not None:
        run_mode = False
        parameter[g] = args[g]

if not run_mode:
    _, _ = convert_parameter(raw_data=True)

class FileInputControl(ft.Stack):
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

    @value.setter
    def setdisabled(self, e):
        self.disabled = e
        self.text_field.disabled = e
        self.pick_button.disabled = e
        self.text_field.update()
        self.pick_button.update()

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
    page.title = 'Transfer timing subtitles by luudanmatcuoi v2.0.0'
    page.window.min_width = 800
    page.padding = 10
    page.window.icon = "dango.ico"
    page.size = 10
    page.scroll = "auto"
    page.window.center()

    def handle_window_event(e):
        if e.data == "close":
            global is_quit
            is_quit = True
            page.window.prevent_close = False
            page.window.close()

    page.window.prevent_close = True
    page.window.on_event = handle_window_event

    def pick_files(e, file_type, control_to_update):
        file_picker = ft.FilePicker(
            on_result=lambda e: setattr(control_to_update, "value", e.files[0].path if e.files else "")
        )
        # page.overlay.append(file_pickera)
        file_picker.pick_files(
            allowed_extensions=[file_type] if file_type else None
        )

    def on_sushi_change(e):
        origin_audio_input.setdisabled = not e.control.value
        ocr_audio_input.setdisabled = not e.control.value
        if not e.control.value:
            sync_sign_ocr_sub_cb.value = False
            sync_sign_ocr_sub_cb.disabled = True
        if e.control.value and using_sign_ocr_sub_cb.value:
            sync_sign_ocr_sub_cb.disabled = False
        page.update()

    def on_tag_change_timed(e):
        if e.control.value:
            cmt_sign_timed_sub_cb.disabled = False
        else:
            cmt_sign_timed_sub_cb.disabled = True
            cmt_sign_timed_sub_cb.value = False
        page.update()

    def on_tag_change_ocr(e):
        if e.control.value:
            cmt_sign_ocr_sub_cb.disabled = False
            if sushi_cb.value:
                sync_sign_ocr_sub_cb.disabled = False
        else:
            cmt_sign_ocr_sub_cb.disabled = True
            cmt_sign_ocr_sub_cb.value = False
            sync_sign_ocr_sub_cb.disabled = True
            sync_sign_ocr_sub_cb.value = False
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
            page.window.prevent_close = False
            page.window.close()

    def on_quit(e):
        global is_quit
        is_quit = True
        page.window.prevent_close = False
        page.window.close()

    def slid(e):
        e.control.value = int(e.control.value*100)/100
        e.control.label = str(int(e.control.value*100)/100)
        page.update()

    def mk_tooltip(e):
        return ft.Tooltip(message=default_config["Tooltip"][e], padding=10, border_radius=5, text_style=ft.TextStyle(size=15, color=ft.Colors.SURFACE))

    # Rest of the controls    
    origin_sub_input = FileInputControl(label="Timed sub", value=parameter["origin_sub_path"], 
        icon = "file", tooltip="origin_sub_path" )
    origin_audio_input = FileInputControl(label="Audio/video", value=parameter["origin_audio_path"], 
        disabled = not parameter["is_using_sushi"], tooltip="origin_audio_path", icon = "audio" )
    ocr_sub_input = FileInputControl(label="OCR sub", value=parameter["ocr_sub_path"], 
        icon = "file", tooltip="ocr_sub_path" )
    ocr_audio_input = FileInputControl(label="Audio/video", value=parameter["ocr_audio_path"], 
        disabled = not parameter["is_using_sushi"], icon="audio" , tooltip="ocr_audio_path" )
    output_filename = ft.TextField(
        label="Output",
        value=parameter["output_filename"],
        expand=True,
        border_width=2,
    )
    sushi_cb = ft.Checkbox( label="Using sushi auto sync based on audio", 
        value=parameter["is_using_sushi"], on_change=on_sushi_change, tooltip=mk_tooltip("is_using_sushi") )
    comment_timed_cb = ft.Checkbox( label="Timed sub", value=parameter["comment_timed_sub"], 
        tooltip=mk_tooltip("comment_timed_sub") )
    comment_ocr_cb = ft.Checkbox( label="OCR sub", value=parameter["comment_ocr_sub"],
        tooltip=mk_tooltip("comment_ocr_sub") )
    
    using_sign_timed_sub_cb = ft.Checkbox( label="Use timed sub", value=parameter["is_use_sign_timed"], 
        on_change=on_tag_change_timed, tooltip=mk_tooltip("is_use_sign_timed") )
    cmt_sign_timed_sub_cb = ft.Checkbox( label="comment it", value=parameter["is_cmt_sign_timed"],
        tooltip=mk_tooltip("is_cmt_sign_timed") )
    using_sign_ocr_sub_cb = ft.Checkbox( label="Use OCR sub", value=parameter["is_use_sign_ocr"], 
        on_change=on_tag_change_ocr, tooltip=mk_tooltip("is_use_sign_ocr") )
    cmt_sign_ocr_sub_cb = ft.Checkbox( label="comment it", value=parameter["is_cmt_sign_ocr"], 
        tooltip=mk_tooltip("is_cmt_sign_ocr") )
    sync_sign_ocr_sub_cb = ft.Checkbox( label="sync it (must select video)", value=parameter["is_sync_sign_ocr"], 
        tooltip=mk_tooltip("is_sync_sign_ocr") )

    # same_rate = ft.Slider( on_change= lambda e:slider_change(e,same_rate, True), min=0, max=100, value=parameter["same_rate"], 
    #     divisions=100, expand=True, tooltip=mk_tooltip("same_rate") )
    same_rate = ft.Slider( min=0.0, max=1.0, divisions=100, on_change=slid, 
        value= float(parameter["same_rate"]), expand=True, tooltip=mk_tooltip("same_rate"))
    distance_string_rate = ft.Slider( min=0.0, max=1.0, divisions=100, on_change=slid, 
        value=parameter["distance_string_rate"], expand=True, tooltip=mk_tooltip("distance_string_rate"))
    distance_string_character = ft.Slider( min=0, max=20, divisions=20, label = "{value}",
        value=parameter["distance_string_character"], expand=True, tooltip=mk_tooltip("distance_string_character") )
    framerate = ft.TextField( label="framerate", value=str(parameter["framerate"]), width=200, expand=True, tooltip=mk_tooltip("framerate") )

    frame_distance = ft.Slider( min=0, max=20, divisions=20, label = "{value}",
        value=parameter["frame_distance"], expand=True, tooltip=mk_tooltip("frame_distance") )
    frame_range = ft.Slider( min=5, max=150, divisions=100, label = "{value}",
        value=parameter["frame_range"], expand=True, tooltip=mk_tooltip("frame_range") )
    sample_shift_range = ft.Slider( min=4, max=20, divisions=16, label = "{value}", 
        value=parameter["sample_shift_range"], expand=True, tooltip=mk_tooltip("sample_shift_range") )
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
        "comment_timed_sub": comment_timed_cb,
        "comment_ocr_sub": comment_ocr_cb,
        "is_use_sign_timed": using_sign_timed_sub_cb,
        "is_cmt_sign_timed": cmt_sign_timed_sub_cb,
        "is_use_sign_ocr": using_sign_ocr_sub_cb,
        "is_cmt_sign_ocr": cmt_sign_ocr_sub_cb,
        "is_sync_sign_ocr": sync_sign_ocr_sub_cb,
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
                ft.Row([sushi_cb ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("For Dialogue, comment lines that only appear in: "), comment_timed_cb, comment_ocr_cb]),
                ft.Row([ft.Text("For Sign: ")]),
                ft.Row([using_sign_timed_sub_cb, cmt_sign_timed_sub_cb]),
                ft.Row([using_sign_ocr_sub_cb, cmt_sign_ocr_sub_cb, sync_sign_ocr_sub_cb]),
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
                            ft.Row([ft.Text("frame_distance :"), frame_distance ]),
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
    is_quit = False
    ft.app(target = main_window)
    if is_quit==True:
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
    if min(abs(a.end-b.start),abs(a.start-b.end)) < (parameter["frame_distance"]/parameter["framerate"])*1000:
        return True
    else:
        False

def is_cross_time(x,y,a,b):
    return (abs(x-a)+abs(y-b)) < (abs(y-x)+abs(b-a))

def clean_inline_comment(stri):
    stri = stri.replace("\\N","[")
    stri = re.sub(r"\{[^\\\{\}]+\}","",stri)
    return stri.replace("[","\\N")

def flat_line(l):
    if l is None:
        return ""
    return f"l_{str(l.layer)}_s_{str(l.start)}_e_{str(l.end)}_c_{str(l.is_comment)}_s_{str(l.style)}_n_{str(l.name)}_t_{str(l.text)}"

def is_uppercase(stri):
    stri = stri.replace("-","").strip()
    if stri=="": return False
    if stri[0]==stri[0].lower(): return False
    return True

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

def generate_graph_image(group, listgroup, lum=None, sat=None):
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import base64
    from io import BytesIO
    # Get min and max times for normalization
    start = min([g["start"] for t in listgroup for g in t])
    end = max([g["end"] for t in listgroup for g in t])
    le = abs(end-start)
    # Normalize and assign colors
    graph = group.copy()
    for g in range(len(graph)):
        graph[g]["start_nom"] = int((graph[g]["start"] - start)/le*100//1)
        graph[g]["end_nom"] = int((graph[g]["end"] - start)/le*100//1)
        graph[g]["color"] = gen_color(g, lum, sat)
        graph[g]["level"] = 0
    # Calculate levels to avoid overlaps
    for g in range(len(graph)):
        while True:
            same_level = [graph[ga] for ga in range(g) if graph[ga]["level"] == graph[g]["level"]]
            if any([(abs(sa["start"]-sa["end"]) + abs(graph[g]["start"]-graph[g]["end"]) - 
                   abs(sa["start"]-graph[g]["start"]) - abs(sa["end"]-graph[g]["end"])) > 2 for sa in same_level]):
                graph[g]["level"] += 1
            else:
                break
    max_level = max([g["level"] for g in graph])

    fig, ax = plt.subplots(figsize=((max_level+1)*2, 10))
    # Draw rectangles for each item - with modified y coordinates for vertical flip
    for g in graph:
        height = 0.8  # Bar height
        # Flip the y coordinates (100 - y)
        flipped_start = 100 - g["end_nom"]  # Swap and invert y coordinates
        flipped_height = g["end_nom"] - g["start_nom"]
        
        rect = plt.Rectangle(
            (g["level"], flipped_start), 1, flipped_height,
            facecolor=g["color"],
            alpha=0.8,
            edgecolor='none'
        )
        ax.add_patch(rect)
    # Remove axes, borders, and ticks spines
    plt.axis('off')
    ax.set_xlim(0, max_level+1)
    ax.set_ylim(0, 100)  # Keep same y limits, the flip happens in the coordinate calculation
    for spine in ax.spines.values():
        spine.set_visible(False)
    # Set figure with transparent background
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    # Save figure to BytesIO buffer
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0, transparent=True, dpi=300)
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_base64

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
    # temp = re.sub(r"\{([^\\]+)}", r"[\1]", a_line.text)
    temp = a_line.text.replace("{","[").replace("}","]")
    temp = re.sub(r"\[(\\[^\]]+)\]", r"{\1}", temp)

    match = re.findall(r"({[^{}]+})?([^{}]+)?", temp)
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

from pyvi import ViTokenizer, ViPosTagger

def split_vietnamese_sentence(text):
    if "\\N" in text or "\n" in text: return text
    # Tokenize and POS tag
    tokens = ViTokenizer.tokenize(text).split()
    pos_tags = ViPosTagger.postagging(ViTokenizer.tokenize(text))[1]  
    tokenl = [len(to) for to in tokens]
    textl = len(text)

    def findratio(tokenl, ratio, over=False):
        for t in range(len(tokenl)):
            if (sum(tokenl[:t])+t)/textl>=ratio:
                if over:
                    return t
                else:
                    return t-1
        return len(tokenl)

    def calrate(i):
        tem1 = sum(tokenl[:i]) + i
        tem2 = sum(tokenl[i:]) + len(tokens) - i
        tem3 = 1-min(tem1,tem2)/(textl/2)
        return tem3
    
    i_min = findratio(tokenl,0.4)
    i_max = findratio(tokenl,0.6)

    pos_split = []
    for i in range(i_min,i_max):
        pos = pos_tags[i]
        pos2 = pos_tags[i+1]
        # Dấu câu
        if pos[0] in ["F"] and pos2[0] not in ["F"]:
            pos_split+=[[i, 3+calrate(i),pos, tokens[i] ]]
        # Cắt sau
        elif pos[0] in ["A","E"]:
            pos_split+=[[i, 1+calrate(i),pos, tokens[i] ]]
        # Cắt trước
        elif pos2[0] in ["C","E"]:
            pos_split+=[[i, 1+calrate(i),pos, tokens[i] ]]
        # Cắt sau V
        elif pos[0] in ["V"] and pos2[0] not in ["V"]:
            pos_split+=[[i, 1+calrate(i),pos, tokens[i] ]]
        else:
            pos_split+=[[i, calrate(i),pos, tokens[i] ]]

    pos_split = max(pos_split, key=lambda x: x[1] )[0]
    pos_index = sum(tokenl[: pos_split ])
    tokens = tokens[pos_split+1].replace("_"," ")
    text = text[:pos_index] + text[pos_index:].replace( tokens, "\\N"+tokens, 1)
    return text

def combine_sub(a_group, b_group):
    split_line_threshold = 52
    # Ghép các sub giống nhau hiển thị liên tiếp
    i = 0
    while i+1 < len(b_group):
        if b_group[i + 1] is None: break
        if is_same_sub(b_group[i].text, b_group[i + 1].text) and is_continue_time(b_group[i], b_group[i + 1]):
            b_group[i].end = b_group[i + 1].end
            del b_group[i + 1]
        else:
            i += 1
    # If a_line got \\N -> 
    if "\\N" in a_group[0].text and len(b_group) > 1:
        # Nếu a có 2 dòng và dòng thứ 2 chữ HOA --> ghép bằng xuống dòng
        if is_uppercase(a_group[0].text.split("\\N")[1]):
            def clear_newline(stri):
                stri = re.sub(r"( )*\n( )*"," ",stri)
                stri = re.sub(r"( )*\\N( )*"," ",stri)
                return stri
            b_group[0].text = "\\N".join([clear_newline(t.plaintext) for t in b_group])
            b_group = [b_group[0]]
        # Nếu a có 2 dòng và dòng thứ 2 chữ THƯỜNG --> ghép bằng dâu cách
        else:
            b_group[0].text = " ".join([t.plaintext.strip("\n\r ") for t in b_group])
            b_group = [b_group[0]]
    elif "\\N" not in a_group[0].text and len(b_group) > 1:
        b_group[0].text = " ".join([t.plaintext.strip("\n\r ") for t in b_group])
        b_group = [b_group[0]]

    # Chia lại line nếu b_text quá dài:
    if len(b_group[0].text) > split_line_threshold and "\\N" not in b_group[0].text:
        b_group[0].text = split_vietnamese_sentence(b_group[0].text)
    return b_group

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
    temp_graph = [[{"text":ga.text,"start":ga.start,"end":ga.end} for ga in a_group],b_group]
    graph1 = generate_graph_image( [{"text":ga.text,"start":ga.start,"end":ga.end} for ga in a_group], temp_graph, lum=3/5 )
    graph2 = generate_graph_image( b_group, temp_graph,lum=2/5,sat=2/3)
    bo=[]
    for b in b_group:
        bo+=[ pysubs2.SSAEvent(start=pysubs2.make_time(ms=b["start"]), end=pysubs2.make_time(ms=b["end"]), text=b["text"]) ]

    return a_group, bo, [graph1, graph2]

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

def shift_sign_using_video(video_path, ocr_signs):
    import cv2
    import numpy as np
    from tqdm import tqdm
    import imagehash
    from PIL import Image

    def process_img(image1, image2):
        """
        Alternative comparison using difference hash (good for transformed images).
        """
        image1_rgb = cv2.cvtColor(image1, cv2.COLOR_BGR2RGB)
        image2_rgb = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
        
        pil_img1 = Image.fromarray(image1_rgb)
        pil_img2 = Image.fromarray(image2_rgb)
        
        hash1 = imagehash.dhash(pil_img1, hash_size=8)
        hash2 = imagehash.dhash(pil_img2, hash_size=8)
        
        hash_diff = hash1 - hash2
        max_diff = len(hash1.hash) ** 2
        similarity = 1 - (hash_diff / max_diff)
        
        return similarity

    # Use perceptual hash by default (best balance of speed and accuracy)
    compare_func = process_img

    vidcap1 = cv2.VideoCapture(parameter["origin_audio_path"])
    vidcap2 = cv2.VideoCapture(video_path)
    fps1 = vidcap1.get(cv2.CAP_PROP_FPS)
    fps2 = vidcap2.get(cv2.CAP_PROP_FPS)
    print("fps of 2 videos: ", fps1, fps2)

    for ocr_sign in ocr_signs:
        frame_range = int(parameter["frame_range"])
        sample_shift_range = int(parameter["sample_shift_range"])

        # Video2 (reference video)
        start_shift_time = ocr_sign["line"].start - (sample_shift_range//2)/fps2*1000
        if start_shift_time < 0:
            vidcap2.set(cv2.CAP_PROP_POS_MSEC, 0)
        else:
            vidcap2.set(cv2.CAP_PROP_POS_MSEC, start_shift_time)
        
        ocr_images = []
        
        # Collect reference frames
        while True:
            for i in range(sample_shift_range):
                if start_shift_time + i/fps2*1000 + 1 < 0:
                    image = np.zeros((144, 256, 3), dtype=np.uint8)  # Note: adjusted dimensions
                else:
                    success, image = vidcap2.read()
                    if not success:
                        image = np.zeros((144, 256, 3), dtype=np.uint8)
                    else:
                        # Resize for consistent comparison
                        image = cv2.resize(image, (256, 144))
                ocr_images.append(image)

            # Check if sample range is sufficient (using higher threshold for hash comparison)
            if compare_func(ocr_images[0], ocr_images[-1]) > 0.95:
                if compare_func(ocr_images[1], ocr_images[-1]) > 0.95:
                    sample_shift_range += 4
                    print("Sample images are too similar, extend sample_shift_range to", sample_shift_range)
                    ocr_images = []  # Reset and collect new samples
                    
                    # Reset video position
                    if start_shift_time < 0:
                        vidcap2.set(cv2.CAP_PROP_POS_MSEC, 0)
                    else:
                        vidcap2.set(cv2.CAP_PROP_POS_MSEC, start_shift_time)
                else:
                    break
            else:
                break

        # Main comparison loop
        while True:
            start_set_video1 = start_shift_time - frame_range/fps1*1000
            if start_set_video1 < 0:
                vidcap1.set(cv2.CAP_PROP_POS_MSEC, 0)
            else:
                vidcap1.set(cv2.CAP_PROP_POS_MSEC, start_set_video1)
            
            database_score = [[] for i in range(sample_shift_range)]
            
            # Compare frames from video1 against reference frames
            for frame_number in tqdm(range(-frame_range, frame_range)):
                if start_shift_time + frame_number/fps1*1000 + 1 < 0:
                    image1 = np.zeros((144, 256, 3), dtype=np.uint8)
                else:
                    success, image1 = vidcap1.read()
                    if not success:
                        image1 = np.zeros((144, 256, 3), dtype=np.uint8)
                    else:
                        # Resize for consistent comparison
                        image1 = cv2.resize(image1, (256, 144))
                
                # Compare against all reference images
                for i in range(len(database_score)):
                    similarity_score = compare_func(image1, ocr_images[i])
                    database_score[i].append(similarity_score)

            # Find best alignment
            compare_database = []
            for g in range(len(database_score[0]) - sample_shift_range):
                total_score = sum([database_score[t][g + t] for t in range(sample_shift_range)])
                compare_database.append(total_score)
            
            temp_compare_database = max(compare_database, default=0)
            
            # Adjusted threshold for hash-based comparison (hashes are generally more different than SSIM)
            min_threshold = sample_shift_range * 0.7  # Lower threshold for hash comparison
            
            if temp_compare_database < min_threshold and frame_range < 200:
                frame_range += 50
                print("Result are suspicious, extend frame_range to", frame_range)
                continue
            else:
                best_shift = compare_database.index(temp_compare_database) - frame_range
                ocr_sign["compare_database"] = best_shift
                
            print("Shift group '", re.sub(r"\{.+\}", "", ocr_sign["group"][0].text), "' ", best_shift, "frames")
            break

    return ocr_signs, fps1

def shift_op_ed(op_sub_path, op_sub, op_start, op_end, src_stream):
    # Get absolute video path
    def get_video_path_from_ass(ass_file_path):
        ass_directory = os.path.dirname(os.path.abspath(ass_file_path))
        op_sub = pysubs2load(ass_file_path)
        try:
            op_sub = op_sub.aegisub_project
            relative_video_path = op_sub["Video File"]
        except:
            return "", False
                    
        path_parts = relative_video_path.replace('\\', '/').split('/')
        current_path = ass_directory.split(os.sep)
        for part in path_parts:
            if part == '..':
                if current_path:
                    current_path.pop()
            elif part and part != '.':
                current_path.append(part)
        absolute_video_path = os.path.normpath(os.sep.join(current_path))    
        return absolute_video_path, True

    video_path, result = get_video_path_from_ass(op_sub_path)
    if not result: return "ass file don't have video file", False

    if not os.path.exists(video_path+".wav"):
        dst_demuxer = sushi.Demuxer(video_path)
        dst_demuxer.set_audio(stream_idx=None, output_path=video_path+".wav", sample_rate=720)
        dst_demuxer.demux()
    dst_stream = sushi.WavStream(video_path+".wav", 1200, 'uint8')
    sample = dst_stream.get_substream(op_start/1000, op_end/1000)
    diff, new_op_start = src_stream.find_substream( sample, src_stream.duration_seconds/2 , src_stream.duration_seconds+10 )
    if diff> 0.4:
        return "OP_ED from {op_sub_path} not in timed video file", False

    # Make ocr_signs for shifting using video/picture
    new_op_start = new_op_start*1000
    new_op_end = new_op_start + (op_end-op_start)
    sample_event = pysubs2.SSAEvent( start=new_op_start , end=new_op_end, text="sample")
    op_signs = [{'id': 0, 'start':new_op_start , 'end':new_op_end , 'line':sample_event , 'group': [sample_event]}]
    ocr_signs, fps1 = shift_sign_using_video(video_path, op_signs)
    compare_database = ocr_signs[0]["compare_database"]
    diff_time = new_op_start-op_start + compare_database/fps1*1000

    return diff_time, True

############################################################################################
#### ------------------------------------- START ------------------------------------- #####
############################################################################################

### Sushi to sync sub by audio
if parameter["is_using_sushi"]:
    class Sushi_args_obj: window=10; max_window=30; rewind_thresh=5; grouping=True; max_kf_distance=2; kf_mode='all'; smooth_radius=3; max_ts_duration=1001.0/24000.0*10; max_ts_distance=1001.0/24000.0*10; plot_path=None; sample_type='uint8'; sample_rate=12000; src_audio_idx=None; src_script_idx=None; dst_audio_idx=None; cleanup=True; temp_dir=None; chapters_file=None; dst_keyframes=None; src_keyframes=None; dst_fps=None; src_fps=None; dst_timecodes=None; src_timecodes=None; verbose=False
    ocr_sub_sushi_path = parameter["ocr_sub_path"][:-4]+".ocr_sushi."+parameter["ocr_sub_path"][-3:]
    if not os.path.exists(ocr_sub_sushi_path):
        sushi_args = Sushi_args_obj()
        sushi_args.source = parameter["ocr_audio_path"]
        sushi_args.destination = parameter["origin_audio_path"]
        sushi_args.script_file = parameter["ocr_sub_path"]
        sushi_args.output_script = ocr_sub_sushi_path
        sushi_args.cleanup = False
        print(sushi_args)
        sushi.run(sushi_args)
else:
    ocr_sub_sushi_path = parameter["ocr_sub_path"]

# Load 2 file
eng_sub = pysubs2load(parameter["origin_sub_path"])
ocr_sub = pysubs2load(ocr_sub_sushi_path)
if parameter["custom_shift"] != 0 and not parameter["is_using_sushi"]:
    ocr_sub.shift(ms=parameter["custom_shift"])

# Import dictionary type to eng_sub actor
for i_s in range(len(eng_sub)):
    old_name = eng_sub[i_s].name
    eng_sub[i_s].name = convert_actor( {"oldname":old_name, "id":str(i_s+1)} )

# Eliminate all 'dialogue sign' line from eng_sub
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

# Eliminate all comment line from eng_sub
comment_group = []
i_eng = 0
while i_eng < len(eng_sub):
    if eng_sub[i_eng].is_comment:
        eng_sub[i_eng].name = eng_sub[i_eng].name+"__tag:comment"
        comment_group += [eng_sub[i_eng]]
        del eng_sub[i_eng]
    else:
        i_eng += 1

# Create timed_map using sushi for open mkv inside webpage
sample_subs = pysubs2.SSAFile.from_string("", format_="srt")
for eng in eng_sub:
    actor_id = str(convert_actor(eng.name)["id"])
    sample_subs += [pysubs2.SSAEvent(start=pysubs2.make_time(ms=eng.start), end=pysubs2.make_time(ms=eng.end), text=actor_id)]
sample_subs.save(parameter["ocr_sub_path"][:-4]+".map.srt")
if parameter["is_using_sushi"]:
    class Sushi_args_obj: window=10; max_window=30; rewind_thresh=5; grouping=True; max_kf_distance=2; kf_mode='all'; smooth_radius=3; max_ts_duration=1001.0/24000.0*10; max_ts_distance=1001.0/24000.0*10; plot_path=None; sample_type='uint8'; sample_rate=12000; src_audio_idx=None; src_script_idx=None; dst_audio_idx=None; cleanup=True; temp_dir=None; chapters_file=None; dst_keyframes=None; src_keyframes=None; dst_fps=None; src_fps=None; dst_timecodes=None; src_timecodes=None; verbose=False
    reverse_sub_sushi_path = parameter["ocr_sub_path"][:-4]+".timed_map.srt"
    if not os.path.exists(reverse_sub_sushi_path):
        sushi_args = Sushi_args_obj()
        sample_subs.save(parameter["ocr_sub_path"][:-4]+".ocr_reverse_sample_sushi.srt")
        sushi_args.source =  parameter["origin_audio_path"]
        sushi_args.destination = parameter["ocr_audio_path"]
        sushi_args.script_file = parameter["ocr_sub_path"][:-4]+".ocr_reverse_sample_sushi.srt"
        sushi_args.output_script = reverse_sub_sushi_path
        sushi_args.cleanup = False
        print(parameter)
        sushi.run(sushi_args)
        os.remove( parameter["ocr_sub_path"][:-4]+".ocr_reverse_sample_sushi.srt" ) 
else:
    sample_subs.save(parameter["ocr_sub_path"][:-4]+".timed_map.srt")

sample_subs = pysubs2load( parameter["ocr_sub_path"][:-4]+".timed_map.srt" )
if parameter["custom_shift"] != 0 and not parameter["is_using_sushi"]:
    sample_subs.shift(ms=parameter["custom_shift"])
timed_map = {}
for sam in sample_subs:
    timed_map[sam.text] = sam.start

if parameter["is_create_map_only"]:
    exit()

# Detect most layer using
layer_eng_sub = [eng.layer for eng in eng_sub if eng.layer!=0]
if len(layer_eng_sub)>0:
    layer_eng_sub = max(set(layer_eng_sub), key=layer_eng_sub.count)
else:
    layer_eng_sub = 0

# Filter sub ocr : Remove empty lines, filter rules (find and replace), Caution unexpected characters
try:
    f = open(os.path.join(root_folder, "filter_rules.txt" ), "r", encoding="utf-8")
    rules = [g.replace("\\n", "\\\\N") for g in f.read().split("\n") if len(g) > 0]
    rules = [g.split("________") for g in rules if "#" not in g[0]]
    f.close()
except:
    rules = []

# Check if characters parameter in default.yml is right
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
        if i_ocr == len(ocr_sub): continue
    if any(["\\" + tag + "(" in ocr_sub[i_ocr].text for tag in ["pos", "move", "org", "clip"]]):
        ocr_signs += [ocr_sub[i_ocr]]
        del ocr_sub[i_ocr]
        continue
    # Filter rules Section
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
        temp_print = "Caution unexpected characters:\t" + " ".join(match) + "\t" + ocr_sub[i_ocr].text
        utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
        print(temp_print, file=utf8stdout)

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
web_groups = []
while i_group < len(group):
    a = []
    b = []
    a += [group[i_group]["eng"]]
    b += [group[i_group]["ocr"]]

    # Check Following group has same line as eng or ocr ?
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

    # Switch case a, b in multi conditions.
    web_group = {"web_id":len(web_groups), "type": None, "group_a":a, "group_b":b, "graphic":[] }
    if len(a) == 0:
        web_group["type"] = "from_ocr"

    elif len(b) == 0:
        web_group["type"] = "from_timed"
        web_group["group_b"] = [pysubs2.SSAEvent( start=0 , end=0, text="") for w in web_group["group_a"] ]

    elif len(a) == 1 and len(b) == 1:
        if len(b[0].text) > 62:
            web_group["group_b"][0].text = split_vietnamese_sentence( web_group["group_b"][0].text )
        web_group["type"] = ""

    elif len(a) == 1 and len(b) > 1:
        web_group["type"] = "combine_sub"
        web_group["group_b"] = combine_sub(a, b)

    elif len(a) > 1:
        web_group["type"] = "split_sub"
        a, b, graph = split_sub(a, b)
        web_group["group_a"] = a
        web_group["group_b"] = b
        web_group["graphic"] = graph

    web_groups+=[web_group]

app = Flask(__name__)
server_thread = None
shutdown_flag = False

@app.route('/')
def index():
    til = Path(parameter["origin_sub_path"])
    til = str(til.name)
    template_string = """
<!DOCTYPE html>
<html>
<head>
    <title>Sync Timing Subtitles</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f5f5f5;
            padding: 0em; 12em;
        }
        .group-container {
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .columns {
            display: flex;
            justify-content: space-between;
        }
        .column {
            width: 50%;
        }
        .event {
            display: flex;
            flex-direction: column;
            background-color: #f9f9f9;
            padding: 5px 20px;
            margin-bottom: 5px;
            border-radius: 4px;
            position: relative;
        }
        .event-time {
            font-size: 0.6em;
            color: #666;
            width: 50%;
        }
        .event-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-top: 2px;
        }
        .event-text {
            flex-grow: 1;
            white-space: nowrap;
            line-height: 1.2em;
        }
        .event-text-b {
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        .event-function {
            margin-left: 10px;
            background-color: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 3px;
            padding: 0px 8px;
            cursor: pointer;
            height: 28px;
            align-self: right;
        }
        .event-copy:hover {
            background-color: #e0e0e0;
        }
        .column_graph {
            min-width: 8%;
            display: flex;
            flex-direction: column;
            overflow-x: auto;
            padding: 0px 10px;
        }
        .group-type {
            font-size: 0.8em;
            color: #666;
            text-align: center;
        }
        .graph_area {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: space-around;
            padding: 5px 0px;
            overflow-x: auto;
        }
        .graph-image {
            height: 100px;
        }
        .time-marker {
            position: absolute;
            height: 100%;
            background-color: rgba(0, 123, 255, 0.3);
            border: 1px solid rgba(0, 123, 255, 0.6);
            border-radius: 2px;
        }
        .empty-message {
            display: grid;
            justify-content: center;
            align-items: center;
            color: #999;
            font-size: 1.5rem;
            font-style: italic;
        }
        .submit-container {
            margin-top: 20px;
            text-align: center;
            padding: 15px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .submit-button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0px 10px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 1s;
        }
        .scroll-button {
          position: fixed;
          bottom: 1%;
          right: 1%;
          outline: none;
          border: none;
          cursor: pointer;
          user-select: none;
          display: grid;
          grid-template-columns: auto auto;
          place-items: center;
          pointer-events: none;
          opacity: 0;
          transition: opacity 500ms ease;
          -webkit-tap-highlight-color: transparent; 
        }
        .show-btn {
          opacity: 1 !important;
          pointer-events: all !important;
        }
    </style>
</head>
<body>
    <div>
        <h3>Sync Timing Subtitles: {{title}}</h3>
    </div>
    <div id="groups-container">
        <!-- Groups will be populated here -->
    </div>
    <div class="submit-container">
        <button id="submit-button" class="submit-button">Submit</button>
    </div>
    <div class="scroll-button ">
        <button id="hide-button" class="submit-button" onclick="hide_button()">Hide/Show normal group</button>
        <button id="gototop" class="submit-button" title="Go to topGo to top">Go to top</button> 
    </div>

    <script>
        // Function to create the graph images section
        function createGraphImagesHtml(graphImages) {
            if (!graphImages || graphImages.length === 0) {
                return '<div class="empty-message"></div>';
            }
            
            let html = '';
            graphImages.forEach(imageBase64 => {
                html += `<img src="data:image/png;base64,${imageBase64}" class="graph-image" alt="Graph">`;
            });
            
            return html;
        }

        // Function to create a group display
        function createGroupHtml(group) {
            const groupA = group.group_a;
            const groupB = group.group_b;
            const colorA = group.color_a;
            const colorB = group.color_b;
            const graphImages = group.graphic || [];
            
            let html = `
                <div class="group-container" data-group-id="${group.web_id}" data-group-type="${group.type}"=>
                    <div class="columns">
                        <div class="column">
                            ${groupA.length > 0 ? groupA.map((event, index) => {
                            return `<div class="event" data-group="a" data-index="${index}"}" style="border-right: 5px solid ${colorA[index]};">
                                    <div class="event-time">${event.start} > ${event.end} 
                                    <button onclick='call_player("${event.map}")'>Open</button>
                                    </div>
                                    <div class="event-content">
                                        <div class="event-text" " >${event.text}</div>
                                        <button class='event-copy' onclick='copy_button(this)' >Copy</button>
                                    </div>
                                </div>
                            `}).join('') : ''}
                        </div>
                        <div class="column_graph">
                            <span class="group-type">${group.type}</span>
                            <div class="graph_area">
                                ${createGraphImagesHtml(graphImages)}
                            </div>
                        </div>
                        
                        <div class="column">
                            ${groupB.length > 0 ? groupB.map((event, index) => {
                            let functionbutton = "";
                            if ( group.type === 'split_sub' ) {
                                functionbutton = "<button class='event-copy' onclick='combine_button(this)'>Combine</button>"
                            } else {
                                functionbutton = "<button class='event-copy' onclick='copy_button(this)' >Copy</button>"
                            }
                            let textColorB = index >= groupA.length ? 'color: gray;' : '';
                            return `<div class="event" data-group="b" data-index="${index}" style="border-left: 5px solid ${colorB[index]}">
                                    <div class="event-time">${event.start} > ${event.end}</div>
                                    <div class="event-content">
                                        <div class="event-text event-text-b" block-id="${group.web_id}" line-stt="${index}" style="${textColorB}" contenteditable>${event.text}</div>
                                        ${functionbutton}
                                        <button class="event-function" onclick="clear_button(this)" >Clear</button>
                                    </div>
                                </div>
                            `}).join('') : ''}
                        </div>
                    </div>
                </div>
            `;
            
            return html;
        }

        let globalData = [];

        // Fetch data and populate the page
        function reload_data() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    globalData = data;
                    const container = document.getElementById('groups-container');
                    data.forEach(group => {
                        container.innerHTML += createGroupHtml(group);
                    });
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    document.getElementById('groups-container').innerHTML = '<div class="error">Error loading data</div>';
                });
        }

        reload_data();

        // Function for hide/show normal group
        function hide_button() {
            var normal_group = document.querySelectorAll("[data-group-type='']");
            normal_group.forEach(group => {
                  if (group.style.display === "none") {
                      group.style.display = "block";
                  } else {
                      group.style.display = "none";
                  }
            });
        }

        // Function to call player
        function call_player(ids) {
            fetch('/play', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({"id": ids })
            })
            .then(response => response.json())
            .then(console.log(call_id))
            .catch(error => {
               console.log(call_id)
            });
        }


        // Function to concatenate current line with next line
        function combine_button(button) {
            var textblock = button.closest('.column');
            var this_text = button.previousElementSibling;
            var thisid = parseInt(this_text.getAttribute("line-stt"));
            var textlines = textblock.querySelectorAll(".event-text");

            textlines.forEach(lines => {
                var temp_id = parseInt(lines.getAttribute("line-stt"));
                if (temp_id<=thisid) { }
                else if ( temp_id-thisid === 1 ) {
                    this_text.innerHTML = this_text.innerHTML + "<br>" + lines.innerHTML;
                    lines.innerHTML = "";
                }
                else if ( temp_id-thisid > 1 ) {
                    var previous_id = String(temp_id-1)
                    var templine = textblock.querySelector("div[line-stt='" + previous_id + "']")
                    templine.innerHTML = lines.innerHTML;
                    lines.innerHTML = "";
                }
            });
        };

        // Function for scroll button
        const scrollButton = document.querySelector(".scroll-button");
        window.addEventListener("scroll", () => {
          window.pageYOffset > 100
            ? scrollButton.classList.add("show-btn")
            : scrollButton.classList.remove("show-btn");
        });
        const gototop = document.querySelector("#gototop");
        gototop.addEventListener("click", () => {
          window.scrollTo({
            top: 0,
            behavior: "smooth" // for smoothly scrolling
          });
        });

        // Add event listener to copy button
        function copy_button(element) {
          var copyText = element.previousElementSibling;
          navigator.clipboard.writeText(copyText.innerHTML);
        } 

        // Add event listener to clear button
        function clear_button(element) {
          var clearText = element.previousElementSibling.previousElementSibling;
          clearText.innerText = "";
        } 

        function shutdown_tab() { 
            document.getElementById("submit-button").innerHTML = "Request sent!";
        }

        // Add event listener to submit button
        document.getElementById('submit-button').addEventListener('click', function() {
            eventElements = document.getElementsByClassName("event-text")
            for (let i = 0; i < eventElements.length; i++) {
              const element = eventElements[i];
              if (element.hasAttribute("block-id")) {
                // Extract the block-id attribute and innerHTML
                const blockId = parseInt(element.getAttribute("block-id"));
                const lineId = parseInt(element.getAttribute("line-stt"));
                const content = element.innerHTML;
                globalData[blockId].group_b[lineId]["text"] = content;
              }
            }
            fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(globalData)
            })
            .then(response => response.json())
            .then(data => { shutdown_tab(); })
            .catch(error => {
                shutdown_tab();
            });
        });
    </script>
</body>
</html>
"""
    return render_template_string(template_string, groups=web_groups, title=til)

@app.route('/data')
def get_data():
    def make_dict(event, amap = False):
        abaka = {
            "start": pysubs2.time.ms_to_str(event.start),
            "start_ms": event.start,
            "end": pysubs2.time.ms_to_str(event.end),
            "end_ms": event.end,
            "text": event.text.replace("\\N","\n").replace("\n","<br>"),
            }
        if amap:
            actor_id = str(convert_actor(event.name)["id"])
            abaka["map"] = timed_map[actor_id],
        return abaka

    obj_items = []
    for item in web_groups:
        obj_item = {
            'web_id': item['web_id'],
            'type': item['type'],
            'graphic': item['graphic'],
            'group_a': [make_dict(event, amap=True) for event in item['group_a']],
            'group_b': [make_dict(event) for event in item['group_b']],
        }

        if item["type"] in ["from_ocr",""]:
            obj_item["color_a"] = ["#fff"]*len(item["group_a"])
        elif item["type"] in ["from_timed"]:
            obj_item['color_a'] = ["#ffff33"]*len(item["group_a"])
        else:
            obj_item['color_a'] = [gen_color(ie,lum=3/5) for ie in range(len(item['group_a']))]

        if item["type"] in ["from_timed",""]:
            obj_item["color_b"] = ["#fff"]*len(item["group_b"])
        else:
            obj_item['color_b'] = [gen_color(ie,lum=2/5,sat=2/3) for ie in range(len(item['group_b']))]
        obj_items.append(obj_item)
    return json.dumps(obj_items)


@app.route('/play', methods=['POST'])
def player():
    web_return = request.json
    call_id = str(int(web_return["id"])-100)
    file_p = parameter["ocr_audio_path"]
    os.system(f'start mpc-hc.exe "{file_p}" /start {call_id} ')
    return "Okie"

        

@app.route('/submit', methods=['POST'])
def submit():
    web_return = request.json
    global best_subtitle
    if len(web_return) != len(web_groups): 
        print(len(web_return) , len(web_groups), "aaaaaaaaaaaaaaaa")
        return "Not okay"
    for w in range(len(web_return)):
        a = web_groups[w]["group_a"]
        b = web_return[w]["group_b"]

        # Filter output
        for bi in range(len(b)):
            b[bi]["text"] = b[bi]["text"].replace("<br>","\n")

        # Handle multi type
        if web_groups[w]["type"]=="from_ocr":
            for i in range(len(b)):
                try:
                    ids = convert_actor(best_subtitle[-1].name)["id"]
                except:
                    ids = 0
                b[i] = pysubs2.SSAEvent(
                    start=b[i]["start_ms"], 
                    end=b[i]["start_ms"],
                    text = b[i]["text"],
                    name = convert_actor({"tag":"from_ocr","oldname":"","id":ids}),
                    layer = layer_eng_sub,
                    type = "Comment",
                    )
            best_subtitle += b

        elif web_groups[w]["type"]=="from_timed":
            for i_s in range(len(a)):
                a[i_s].name = a[i_s].name+"__tag:from_timed"
            if parameter["comment_timed_sub"]:
                best_subtitle += [apply_sub(tg, "") for tg in a]
            else:
                best_subtitle += a

        elif web_groups[w]["type"]=="":
            for ai in range(len(a)):
                a[ai].name = a[ai].name+"__tag:"
            for i_s in range(len(a)):
                best_subtitle += [apply_sub(a[i_s], b[i_s])]

        elif web_groups[w]["type"]=="combine_sub":
            for i_s in range(len(a)):
                a[i_s].name = a[i_s].name+"__tag:combine_sub"
                best_subtitle += [apply_sub(a[i_s], b[i_s])]

        elif web_groups[w]["type"]=="split_sub":
            for i_s in range(len(a)):
                a[i_s].name = a[i_s].name+"__tag:split_sub"
                best_subtitle += [apply_sub(a[i_s], b[i_s])]
    # Shutdown flask server
    global shutdown_flag
    shutdown_flag = True
    sys.exit(0)

def run_server():
    app.run(host='127.0.0.1', port=5000)

if __name__ == '__main__':
    # signal.signal(signal.SIGINT, signal_handler)
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    while not shutdown_flag:
        time.sleep(1)

# Find any sub from_eng, from_sub line that alone (not have line respective)
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

################# Transfer signs 
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


if parameter["is_use_sign_timed"] and len(eng_signs)>0:
    for sign in eng_signs:
        if parameter["is_cmt_sign_timed"]:
            sign.type = "Comment"
        best_subtitle += [sign]


if parameter["is_use_sign_ocr"] and len(ocr_signs)>0:

    # Find last id in best_subtitle
    last_best_subtitle_id = max([convert_actor(ga.name)["id"] for ga in best_subtitle])
    step_id = 2
    if not parameter["is_sync_sign_ocr"]:
        # Add ocr_signs
        for ocr_sign in ocr_signs:
            ac = {"id":last_best_subtitle_id+step_id/10000, "tag":"sign","oldname":str(ocr_sign.name)}
            step_id+=1
            ocr_sign.name=convert_actor(ac)
            best_subtitle+=[ocr_sign]
    else:
        ocr_sub_or = pysubs2load(parameter["ocr_sub_path"])

        # Create ocr signs -> grouping -> start shift
        ocr_signs = []
        for i_ocr in range(len(ocr_sub_or)):
            if any(["\\" + tag + "(" in ocr_sub_or[i_ocr].text for tag in ["pos", "move", "org", "clip"]]):
                ocr_signs += [ocr_sub_or[i_ocr]]
        ocr_signs = grouping_signs(ocr_signs)
        ocr_signs, fps1 = shift_sign_using_video( parameter["ocr_audio_path"], ocr_signs)

        #Shift time, change actor name
        for ocr_sign in ocr_signs:
            for ocr_sign_el in ocr_sign["group"]:
                ac = {"id":last_best_subtitle_id+step_id/10000, "tag":"sign","oldname":str(ocr_sign_el.name)}
                step_id+=1
                ocr_sign_el.name=convert_actor(ac)
                ocr_sign_el.shift(frames=ocr_sign["compare_database"],fps=fps1)
                best_subtitle+=[ocr_sign_el]

for comment in comment_group:
    best_subtitle += [comment]


op_ed_folder = "D:\\Sakura\\op_ed"
try:
    op_ed_listfiles = [os.path.join(op_ed_folder, f) for f in os.listdir(op_ed_folder) if os.path.isfile(os.path.join(op_ed_folder, f) ) and "ass" == f[-3:].lower()]
except:
    op_ed_listfiles = []
if not os.path.exists(parameter["origin_audio_path"]+".wav"):
    src_demuxer = sushi.Demuxer(parameter["origin_audio_path"])
    src_demuxer.set_audio(stream_idx=None, output_path=parameter["origin_audio_path"]+".wav", sample_rate=1200)
    src_demuxer.demux()
src_stream = sushi.WavStream(parameter["origin_audio_path"]+".wav", 1200, 'uint8')

print(op_ed_listfiles)
for op_ed_path in op_ed_listfiles:
    op_sub = pysubs2load(op_ed_path)
    if len(op_sub)<2: continue
    op_start = op_sub[0].start
    op_end = op_sub[-1].end
    for i_op in range(len(op_sub)):
        if not op_sub[i_op].is_comment:
            op_start = min(op_start, op_sub[i_op].start)
            op_end = max(op_end, op_sub[i_op].end)
    diff_time, res = shift_op_ed(op_ed_path, op_sub, op_start, op_end, src_stream)
    if not res:
        print(diff_time)
    else:
        new_op_start = op_start+diff_time
        new_op_end = op_end+diff_time
        # Remove every lines of best_subtitle in op_ED area
        i_sub = 0
        while i_sub<len(best_subtitle):
            if is_cross_time( best_subtitle[i_sub].start, best_subtitle[i_sub].end, new_op_start, new_op_end):
                del best_subtitle[i_sub]
            else:
                i_sub+=1
        # Add new op_ed sub       
        last_best_subtitle_id = max([convert_actor(ga.name)["id"] for ga in best_subtitle])+1
        for i_op in range(len(op_sub)):
            op_sub[i_op].shift(ms=diff_time)
            ac = {"id":last_best_subtitle_id, "tag":"op_ed","oldname":str(op_sub[i_op].name)}
            op_sub[i_op].name=convert_actor(ac)
            last_best_subtitle_id+=1/1000
            best_subtitle += [op_sub[i_op]]


#Sort best_subtitle follow ids (remain order after do xyz stuff): 
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
write_sub = pysubs2load(parameter["origin_sub_path"])
while len(write_sub) > 0:
    del write_sub[0]

# Transfer styles
if parameter["ocr_sub_path"][-3:] in ["ass", "ssa"]:
    style_file = pysubs2load(parameter["ocr_sub_path"])
    write_sub.import_styles(style_file)
for op_ed_path in op_ed_listfiles:
    op_sub = pysubs2load(op_ed_path)
    write_sub.import_styles(op_sub)

for b in best_subtitle:
    write_sub.append(b)

write_sub.save(parameter["output_filename"])

print("DONE :v")
