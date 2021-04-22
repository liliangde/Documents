import tinify
import os


def compress(filePath):
    beforeSize = os.path.getsize(filePath)
    print("开始压缩: %s" % os.path.split(filePath)[-1])
    source = tinify.from_file(filePath)
    source.to_file(filePath)
    print("完成压缩: %s 节约：%skb" % (os.path.split(filePath)[-1], (os.path.getsize(filePath) - beforeSize) / 1024))


def findImage(path):
    for item in os.listdir(path):
        filePath = path + '/' + item
        if os.path.isdir(filePath):
            findImage(filePath)
        elif os.path.isfile(filePath):
            fileType = os.path.splitext(filePath)[-1]
            if fileType == '.jpg' or fileType == '.png' or fileType == '.jpeg':
                # 大于20k的才进行压缩
                if os.path.getsize(filePath) / 1024 > 20:
                    compress(filePath)

        else:
            continue


if __name__ == '__main__':
    tinify.key = 'xcTmdtMSbMXfrpl7PPTYK0Dh30dmKn3h'
    # print(tinify.compression_count)
    findImage('/Users/za/Desktop/ZABusinessRecommend')
