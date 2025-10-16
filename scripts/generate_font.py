import subprocess
from pprint import pprint

# Write Shift JIS file.
a = 'abcdefghijklmnopqrstuvwxyz' \
'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
'~!@#$%^&*()_+[]()' \
'0123456789' \
'あいうえお' \
'かきくけこ' \
'がぎぐげご' \
'さしすせそ' \
'ざじずぜぞ' \
'たちつてと' \
'だぢづでど' \
'なにぬねの' \
'はひふへほ' \
'ばびぶべぼ' \
'ぱぴぷぺぽ' \
'まみむめも' \
'やゆよ' \
'らりるれろ' \
'わをん' \
'ャュョ' \
'アイウエオ' \
'カキクケコ' \
'ガギグゲゴ' \
'サシスセソ' \
'ザジズゼゾ' \
'タチツテト' \
'ダヂヅデド' \
'ナニヌネノ' \
'ハヒフヘホ' \
'バビブベボ' \
'マミムメモ' \
'ヤユヨ' \
'ラリルレロ' \
'ワヲン' \
'ョャュ' \
'日本語' \
'' \
'一ニ三丸' \
'海外の日本人向けの日本語チャンネル、NHKワールド・プレミアムは、国内で放送されているニュース・情報番組、ドラマ、音楽番組、子ども番組、スポーツ中継などから選んだ番組を24時間編成しています。世界のおよその国・地域の約2,4万世帯以上で視聴できます。' \
'衛星からの直接受信により無料で視聴できる、ノンスクランブル時間帯をインターネットでも視聴できます。' \
'国内の主要ニュース、時事番組、スポーツ中継、音楽番組、ラジオドラマなど、ラジオ第1放送の番組を国内と同時に放送し、日本の多彩な情報を伝えます。太平洋・インド洋でマグニチュード7.6以上の地震があり、津波のおそれがある時は、日本語による津波警報を放送します。' \
'NHKワールド JAPANの英語チャンネルは、衛星や各国・地域の放送事業者等を通じて世界に向けて放送しています。また、訪日・在日外国人の日本への理解を促進することを目的として、国内でもCATV/IPTV/ネット事業者に提供しています。衛星から直接受信していただくか、提供先の事業者からの配信サービスをご利用いただくことで、ホテル・旅館客室への導入が可能です。（NHKワールド JAPANの受信は無料です。事業者配信サービスをご利用の場合、別途サービス料が必要となります）導入したホテル・旅館の一覧を公開しています。' \
'敵がアメリカの戸口に迫ったとき、この国は地球規模で猛威を振るう世界的な戦火から身を引いてはいられなかった。海で、陸で、空で、アメリカの兵士たちは枢軸軍の卑劣な攻撃に抗わねばならない。混乱の時は束の間で、眠れる巨人は目を覚まし、自由のために立ち上がるだろう。太平洋の島々で、そして同盟国がアメリカ軍の力を必要とする世界のあらゆる場所で。' \
' ' # spaces would be nice!
a = list(set(a))
a.sort(key=lambda x: ord(x))
a = ''.join(a)
print(len(a))
charset_path = './data/CharSet_shiftjis.txt'
with open(charset_path, 'wb') as fout:
    b = bytearray(a.encode('shift_jis'))
    b.reverse()
    fout.write(b)

from typing import Literal

FontThickness = Literal[100, 400, 800]
Charset = str
Pitch = Literal['default', 'fixed', 'variable']

class FontSettings:
    def __init__(self,
                 name: str,
                 uid: str,
                 face_name: str,
                 height: int,
                 thickness: FontThickness,
                 charset: Charset,
                 italic: bool,
                 antialias: bool, 
                 pitch: Pitch               
                 ):
         self.name = name
         self.uid = uid
         self.face_name = face_name
         self.height = height
         self.thickness = thickness
         self.charset = charset
         self.italic = italic
         self.antialias = antialias
         self.pitch = pitch


class FontGenResult:
    def __init__(self, binary_path: str, tga_path: str):
        self.binary_path = binary_path
        self.tga_path = tga_path


def fontgen(font_settings: FontSettings) -> FontGenResult:
    binary_path = f'./Output/Bin/Fonts/{font_settings.uid}'
    tga_path: str = f'./Output/Fonts/Body/Texture.tga'
    args = [
        './FontGen.exe',
        f'-h{font_settings.height}',
        f'-aa',
        f'-{font_settings.charset}',
        f'"{font_settings.face_name}"', 
        f'"{binary_path}"',
        f'"{tga_path}"',
        charset_path
    ]
    subprocess.call(args)
    # Find and rename the files that were made since it's making everything lowercase for some reason.
    import os
    try:
        os.renames(binary_path.lower(), binary_path)
    except FileNotFoundError:
        pass

    try:
        os.renames(tga_path.lower(), tga_path)
    except FileNotFoundError:
        pass

    return FontGenResult(binary_path, tga_path)


def create_font_xdb(font_settings: FontSettings, path: str):
    import xml.etree.cElementTree as ET
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'wb') as fp:
        font = ET.Element("Font", ObjectRecordId="1000000")

        font.append(ET.Element("Texture", href="Texture.xdb#xpointer(/Texture)"))

        def add_text_element(tag: str, text: str):
            element = ET.Element(tag)
            element.text = text
            return element

        font.append(add_text_element("uid", font_settings.uid))
        font.append(add_text_element("Height", str(font_settings.height)))
        font.append(add_text_element("Thickness", str(font_settings.thickness)))
        font.append(add_text_element("Italic", str(font_settings.italic).lower()))
        font.append(add_text_element("Antialiased", str(font_settings.antialias).lower()))
        font.append(add_text_element("Pitch", font_settings.pitch.upper()))
        font.append(add_text_element("Charset", font_settings.charset.upper()))
        font.append(add_text_element("FaceName", font_settings.face_name))
        font.append(add_text_element("Name", font_settings.name))
        font.append(ET.Element("CharactersFile", href=""))

        tree = ET.ElementTree(font)
        ET.indent(tree, '\t', level=0)
        tree.write(fp, encoding='utf-8', xml_declaration=True)



def gen_bmfont():
    from collections import OrderedDict
    data = OrderedDict()

    # AngelCode Bitmap Font Generator configuration file
    data['fileVersion'] = 1

    # font settings
    data['fontName'] = 'Unifont'
    data['charSet'] = 0
    data['fontSize'] = 18
    data['aa'] = 1
    data['scaleH'] = 100
    data['useSmoothing'] = 1
    data['isBold'] = 0
    data['isItalic'] = 0
    data['useUnicode'] = 1
    data['disableBoxChars'] = 1
    data['outputInvalidCharGlyph'] = 0
    data['dontIncludeKerningPairs'] = 0
    data['useHinting'] = 1
    data['renderFromOutline'] = 0
    data['useClearType'] = 1
    data['autoFitNumPages'] = 0
    data['autoFitFontSizeMin'] = 0
    data['autoFitFontSizeMax'] = 0

    # character alignment
    data['paddingDown'] = 0
    data['paddingUp'] = 0
    data['paddingRight'] = 0
    data['paddingLeft'] = 0
    data['spacingHoriz'] = 1
    data['spacingVert'] = 1
    data['useFixedHeight'] = 0
    data['forceZero'] = 0
    data['widthPaddingFactor'] = 0.0

    # output file
    data['outWidth'] = 256
    data['outHeight'] = 256
    data['outBitDepth'] = 8
    data['fontDescFormat'] = 0
    data['fourChnlPacked'] = 0
    data['textureFormat'] = 'tga'
    data['textureCompression'] = 0
    data['alphaChnl'] = 1
    data['redChnl'] = 0
    data['greenChnl'] = 0
    data['blueChnl'] = 0
    data['invA'] = 0
    data['invR'] = 0
    data['invG'] = 0
    data['invB'] = 0

    # outline
    data['outlineThickness'] = 0

    # selected chars
    data['chars'] = '52736-52825,52829-52991'

    with open('myfont.bmfc', 'w') as fp:
        for key, value in data.items():
            fp.write(f'{key}={value}\n')


if __name__ == '__main__':
    font_settings = FontSettings(
        name='body',
        uid='0E16E454-C6F2-4BE0-A290-BCB0A7D9640C',
        face_name='unifont',
        antialias=False,
        charset='shiftjis',
        height=18,
        pitch='default',
        thickness=100,
        italic=False
    )

    fontgen_result = fontgen(font_settings)
    create_font_xdb(font_settings, f'./Output/Fonts/Body/Font.xdb')

    # TODO: check if mogrify exists; if it doesn't throw an error.
    args = ['mogrify', '-format', 'dds', fontgen_result.tga_path]
    subprocess.call(args)

    from pathlib import Path
    zip_path = Path('/home/colinb/.local/share/Steam/steamapps/common/Blitzkrieg 2 Anthology/Blitzkrieg 2/Data/')
    zip_path /= 'texts_jp'
    zip_path = zip_path.resolve().absolute()

    import shutil
    import os
    shutil.make_archive(str(zip_path), 'zip', './Output')
    os.rename(zip_path.with_suffix('.zip'), zip_path.with_suffix('.pak'))
    # Zip up everything in "Output" and stick it in the right spot.

    gen_bmfont()

    # TODO: invoke BMF
    # TODO: try to generate a font file for Blitzkrieg (just paper over the balues that we don't understand, we can see if it works!)
