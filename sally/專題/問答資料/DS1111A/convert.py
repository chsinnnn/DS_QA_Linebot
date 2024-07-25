import os
import xmltodict
import json

def convert_xml_to_json(xml_folder, json_folder):
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    for filename in os.listdir(xml_folder):
        if filename.endswith('.xml'):
            xml_path = os.path.join(xml_folder, filename)
            json_path = os.path.join(json_folder, filename.replace('.xml', '.json'))

            with open(xml_path, 'r', encoding='utf-8') as xml_file:
                xml_content = xml_file.read()

            json_content = xmltodict.parse(xml_content)
            with open(json_path, 'w', encoding='utf-8') as json_file:
                json.dump(json_content, json_file, ensure_ascii=False, indent=4)

            print(f'Converted {xml_path} to {json_path}')

# 指定你的 XML 檔案夾和 JSON 檔案夾路徑
xml_folder = 'C:/Users/sally/Desktop/專題/dataset/board'
json_folder = 'C:/Users/sally/Desktop/專題/dataset/json'

convert_xml_to_json(xml_folder, json_folder)
