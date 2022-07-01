import os
import re
import sys
import getopt

# 用法示例：python3 FindUnUsedImage.py -p /Users/za/Desktop/zhenaiwang.app

RESULT_FILE_PATH = sys.path[0].strip() + '/' + 'find_un_use_resource.txt'


def getInputParm():
    opts, args = getopt.getopt(sys.argv[1:], '-p:', ['path='])

    # 入参判断
    for opt_name, opt_value in opts:
        if opt_name in ('-p', '--path'):
            # 文件路径
            path = opt_value

    # 必须指定".app"目录
    if not path.endswith('.app'):
        print("\033[0;31;40m请指定.app目录\033[0m")
        exit(1)

    # 判断文件路径存不存在
    if not os.path.exists(path):
        print("\033[0;31;40m输入的文件路径不存在\033[0m")
        exit(1)

    return path


def unzip_asset(paths) -> set:
    image_names = set()
    for path in paths:
        info = os.popen("xcrun --sdk iphoneos assetutil --info %s" % path)
        lines = info.readlines()

        re_image_name = re.compile("    \"Name\" : \".*\"")

        for line in lines:
            result = re_image_name.findall(line)
            if result:
                name = result[0][14:-1]
                if name not in image_names:
                    image_names.add(name)
    return image_names


def get_all_str_in_mac_o(paths) -> set:
    str_class_name = re.compile("\w{16}  (.+)")
    all_str = set()
    for path in paths:
        lines = os.popen('/usr/bin/otool -v -s __TEXT __cstring %s' % path).readlines()
        for line in lines:
            stringArray = str_class_name.findall(line)
            if len(stringArray) > 0:
                tempStr = stringArray[0]
                all_str.add(tempStr)
    return all_str


def check_resource_paths(path):
    all_car_paths = set()
    all_lottie_paths = set()
    all_svgas = set()
    all_mvs = set()
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".car"):
                assets_car_path = os.path.join(root, file)
                all_car_paths.add(assets_car_path)
            if file.endswith(".json"):
                lottie_path = os.path.join(root, file)
                all_lottie_paths.add(lottie_path)
            if file.endswith(".svga"):
                all_svgas.add(file)
            if file.endswith(".mp4") or file.endswith(".mp3") or file.endswith(".aac") or file.endswith(".mov"):
                all_mvs.add(file)

    all_mac_o_paths = set()
    appname = path.split('/')[-1].split('.')[0]
    all_mac_o_paths.add(os.path.join(path, appname))
    frameworks_path = os.path.join(path, "Frameworks")
    for file in os.listdir(frameworks_path):
        if file.startswith("ZA"):
            framework = file.split(".")[0]
            mac_o_path = os.path.join(frameworks_path, file, framework)
            all_mac_o_paths.add(mac_o_path)

    return all_car_paths, all_mac_o_paths, all_lottie_paths, all_svgas, all_mvs


def get_un_use_images(all_car_paths, all_lottie_paths, all_strs):
    all_images = unzip_asset(all_car_paths)

    tmp = all_images - all_strs

    result = set()
    result_contain_number = []
    for r in tmp:
        re_image_name = re.compile(".*[0-9]{1,2}$")
        s = re_image_name.findall(r)
        if s:
            result_contain_number.append(r)
        else:
            result.add(r)

    for r in result_contain_number:
        use = False
        for s in all_strs:
            if len(s) > 6 and s[0: 6] in r:
                use = True
                break
        if not use:
            result.add(r)

    images_in_lottie = get_images_in_lottie(all_lottie_paths)

    return result - images_in_lottie


def get_un_use_svgas(all_svgas, all_strs):
    result = []
    for svga in all_svgas:
        name = svga.split('.')[0]
        use = False
        for s in all_strs:
            if name in s:
                use = True
                break
        if not use:
            result.append(name)
    return result


def get_un_use_mvs(all_mvs, all_strs):
    result = []
    for mv in all_mvs:
        name = mv.split('.')[0]
        use = False
        for s in all_strs:
            if name in s:
                use = True
                break
        if not use:
            result.append(mv)
    return result


def get_un_use_lotties(all_lottie_paths, all_strs):
    result = []
    for lottie_path in all_lottie_paths:
        name = os.path.split(lottie_path)[-1].split('.')[0]
        use = False
        for s in all_strs:
            if name in s:
                use = True
                break
        if not use:
            result.append(name)
    return result


def get_images_in_lottie(all_lottie_paths):
    result = set()
    re_image_name = re.compile("\"p\":\"[\w-]{5,}.png\"")
    for path in all_lottie_paths:
        with open(path, 'r') as f:
            s = re_image_name.findall(f.read())
            if s:
                for r in s:
                    name = r[5: -5]
                    result.add(name)
    return result


def write_to_file(result, title):
    if len(result) == 0:
        return

    f = open(RESULT_FILE_PATH, 'a')
    f.write('\n未使用%s资源如下： \n' % title)

    num = 1
    for r in result:
        showStr = ('%d : %s' % (num, r))
        print(showStr)
        f.write(showStr + "\n")
        num = num + 1
    f.close()


if __name__ == '__main__':

    path = getInputParm()

    all_car_paths, all_mac_o_paths, all_lottie_paths, all_svgas, all_mvs = check_resource_paths(path)
    all_strs = get_all_str_in_mac_o(all_mac_o_paths)

    if os.path.exists(RESULT_FILE_PATH):
        os.remove(RESULT_FILE_PATH)

    # 搜索未使用的lottie
    un_use_lotties = get_un_use_lotties(all_lottie_paths, all_strs)
    print("\n-------------共找到%d个lottie-------------\n" % len(un_use_lotties), un_use_lotties)
    write_to_file(un_use_lotties, "lotties")

    # 搜索未使用的svga
    un_use_svgas = get_un_use_svgas(all_svgas, all_strs)
    print("\n-------------共找到%d个svga-------------\n" % len(un_use_svgas), un_use_svgas)
    write_to_file(un_use_svgas, "svgas")

    # 搜索未使用的音视频
    un_use_mvs = get_un_use_mvs(all_mvs, all_strs)
    print("\n-------------共找到%d个mv-------------\n" % len(un_use_mvs), un_use_mvs)
    write_to_file(un_use_mvs, "mvs")

    # 搜索未使用的图片
    un_use_images = get_un_use_images(all_car_paths, all_lottie_paths, all_strs)
    print("\n-------------共找到%d个image-------------\n" % len(un_use_images), un_use_images)
    write_to_file(un_use_images, "images")

    print("\n-------------检测完成 请查看%s文件-------------\n" % RESULT_FILE_PATH)
