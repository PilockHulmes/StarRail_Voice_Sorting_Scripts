import json
import re
import os
import argparse
from tqdm import tqdm
from pathlib import Path
from glob import glob
from shutil import copy, move
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('-src','--source', type=str, help='未整理数据集目录', required=True)
parser.add_argument('-ver','--version', type=str, help='版本', required=True)
parser.add_argument('-dst','--destination', type=str, help='目标路径', required=True)
parser.add_argument('-lang','--language', type=str, help='语言（可选CHS/EN/JP/KR）', required=True)
parser.add_argument('-m','--mode', type=str, help='模式(复制(cp)/移动(mv))', default="cp")
args = parser.parse_args()

source = str(args.source)
dest = str(args.destination)
language = str(args.language).upper()
ver = str(args.version)
mode = str(args.mode)

if not os.path.exists(dest):
    Path(dest).mkdir(parents=True)

def is_in(full_path, regx):
    if re.findall(regx, full_path):
        return True
    else:
        return False

def is_file(full_path):
    if os.path.exists(full_path):
        return True
    else:
        return  False

def get_support_ver():
    indexs = glob('./Indexs/*')
    support_vers = []
    for vers in indexs:
        version = os.path.basename(vers)
        support_vers.append(version)
    versions = '|'.join(support_vers)
    return versions


def get_support_lang(version):
    if is_in(version, get_support_ver()):
        support_langs = []
        indexs = glob(f'./Indexs/{version}/*')
        for langs in indexs:
            lang_code = os.path.basename(langs).replace(
                "_output.json", "").replace(".json", "")
            support_langs.append(lang_code)
        return support_langs
    else:
        print("不支持的版本")
        exit()


def get_path_by_lang(lang):
    langcodes = get_support_lang(ver)
    path = ['中文 - Chinese', '英语 - English',  '日语 - Japanese', '韩语 - Korean']
    try:
        i = langcodes.index(lang)
        dest_path = path[i]
        lang_code = lang
    except:
        print("不支持的语言")
        exit()
    return lang_code, dest_path


langcode, dest_lang = get_path_by_lang(language)

def ren_player(player, lang):
    langcodes = get_support_lang(ver)
    player_boy_names = ['开拓者(男)', 'Trailblazer(M)', '開拓者(男)', '개척자(남)']
    player_girl_names = ['开拓者(女)', 'Trailblazer(F)', '開拓者(女)', '개척자(여)']
    p_name = player
    if p_name == "playerboy" or p_name == "playergirl":
        if p_name == "playerboy":
            i = langcodes.index(lang)
            p_name = player_boy_names[i]
        if p_name == "playergirl":
            i = langcodes.index(lang)
            p_name = player_girl_names[i]
    else:
        p_name = player
    return p_name

indexfile = Path(f'./Indexs/{ver}/{langcode}.json').read_text(encoding="utf-8")
data = json.loads(indexfile)
for k in tqdm(data.keys()):
    try:
        text = data.get(k).get('ContentText')
        char_name = data.get(k).get('Speaker')
        title_text = data.get(k).get('TitleText')
        if char_name is not None:
            char_name = ren_player(char_name,langcode)
        elif title_text is not None:
            char_name = ren_player(title_text,langcode)
        else:
            char_name = "#Unknown"
        path = data.get(k).get('VoiceName')
        wav_source = f"{source}/{dest_lang}/{path}"
        wav_file = os.path.basename(path)
        if char_name is not None:
            vo_dest_dir = f"{dest}/{dest_lang}/{char_name}"
            vo_wav_path = f"{vo_dest_dir}/{wav_file}"
            if is_file(wav_source) == True:
                if not os.path.exists(vo_dest_dir):
                    Path(f"{vo_dest_dir}").mkdir(parents=True)
                dest_path = vo_wav_path
                if mode.upper() == 'CP':
                    copy(wav_source, dest_path)
                elif mode.upper() == 'MV':
                    move(wav_source, dest_path)
                else:
                    print("模式错误，请选择cp/mv")
                    exit()
    except:
        pass