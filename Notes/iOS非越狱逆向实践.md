[toc]

## 解密
本文主要讲述非越狱逆向的相关问题，而应用解密需要用到越狱手机，故不在此做过多的解释，有兴趣的可以自行查阅相关应用解密的相关文章。我们这里直接从PP助手下载解密后的ipa进行下面的研究，下载下来后可以通过下面命令来检查下载的可执行文件是否已经解密：

```sh
otool -l *** | grep cryptid #***为下载的ipa解压出来后.app文件夹下对应的可执行文件
```
运行上述命令，如果得到的cryptid为0则说明应用已经解密。

## 重签名
### 为什么要重签名？
下图概述了app在启动的时候会检验的一些信息，只有校验成功app才能完成启动：
![](https://github.com/liliangde/Images/blob/main/逆向/appLaunch.png?raw=true)
如上图所示，如果想让目标app能够运行在我们自己的设备上面就必须要用自己的证书和配置文件对目标app进行重签名。

### 重签名的步骤
1. 获取本地证书列表
> ``security find-identity -p codesigning -v``

2. 选取上面获取到的一个证书对目标app目录中的所有的framework和dylib文件签名
> ``codesign -f -s FCAC9070B3B0C736D1D6855D54F806FB99BD5084 ***``

3. 新建一个Xcode工程，选择iOS通用设备，编译生成目标``.app``文件,然后到``.app``文件夹中找到生成``embedded.mobileprovision``配置文件，通过此配置文件生成签名``.app``目录需要的授权文件``entitlements.plist``文件.
> ``security cms -D -i embedded.mobileprovision > profile.plist``
> ``/usr/libexec/PlistBuddy -x -c 'Print :Entitlements' profile.plist > entitlements.plist``

4. 将``entitlements.plist``文件复制到``zhenaiwang.app``同级目录下,然后对``.app``目录签名
> ``codesign -f -s FCAC9070B3B0C736D1D6855D54F806FB99BD5084 --entitlements entitlements.plist ***.app``

5. 将签名后的``.app``打包成ipa
> ``mkdir Payload``
> ``cp -rf ***.app ./Payload``
> ``zip -qr ***.ipa ./Payload``

6. 用Xcode安装ipa到手机

## Xcode调试第三方应用
### 首先了解下应用的大致构建过程，如下图
![](https://github.com/liliangde/Images/blob/main/逆向/appBuild.png?raw=true)

1. 首先创建``.app``目录
2. 生成签名需要用到的``Entitlements.plist``授权文件
3. 编译源文件
4. 链接目标文件
5. 对``.app``目录签名

### 用Xcode运行我们自己的APP
#### 一个词概括：偷梁换柱
1. 新建一个Xcode工程``NewAPP``
2. 删除Xcode默认build生成的``.app``目录
3. 给目标``.app``文件夹中``info.plist`` 中 ``CFBundleExecutable`` 对应的文件添加可执行权限（如果已经有了可执行权限则忽略此步）
4. 修改目标应用``Info.plist``中的bundle ID 为新创建的``NewApp``的bundle ID
4. 将目标``.app``文件拷贝到第2步删除的``.app``的同级目录下
5. 移除目标``.app``目录下的``PlugIns``和``Watch``目录（如果有这两个目录），因为这两个目录下的内容无法被签名
6. 对目标``.app``目录下的所有framework和动态库签名

将上面的步骤编写成shell脚本，添加到Xcode的``Run Script``下面(**注意修改脚本中的目标app的名字**),然后将目标``.app``拖到新建的``NewAPP ``工程目录下，Commend+R运行，至此目标app就可以在我们的Xcode上面运行起来了，脚本代码如下：

```sh
#需要拷贝的目标应用 (*** 需要替换目标app的名字)
TARGET_APP_PATH="${SRCROOT}/***.app"     
#build生成的应用                      
BUILD_APP_PATH="$BUILT_PRODUCTS_DIR/$TARGET_NAME.app"   
#目标app可执行文件的名称       
MATCHO_FILE=$(/usr/libexec/PlistBuddy -c "Print CFBundleExecutable" "$TARGET_APP_PATH/Info.plist")

#删除原目录
rm -rf "$BUILD_APP_PATH" || true
mkdir -p "$BUILD_APP_PATH" || true

#给目标应用目录下的可执行文件添加执行权限
chmod +x "$TARGET_APP_PATH/$MATCHO_FILE"

#修改目标应用Info.plist中的bundle id 为新创建的NewApp的bundle id
/usr/libexec/PlistBuddy -c "Set CFBundleIdentifier $PRODUCT_BUNDLE_IDENTIFIER" "$TARGET_APP_PATH/Info.plist"

#拷贝目标应用替换build生成的应用
cp -rf "$TARGET_APP_PATH/" "$BUILD_APP_PATH/"

#删除PlugIns和Watch
rm -rf "$BUILD_APP_PATH/PlugIns" || true
rm -rf "$BUILD_APP_PATH/Watch" || true

#签名所有framework和动态库
function codesign(){
    for file in `ls $1`;
    do
		extension="${file#*.}"
        if [[ -d "$1/$file" ]]; then
			if [[ "$extension" == "framework" ]]; then
        			/usr/bin/codesign --force --sign "$EXPANDED_CODE_SIGN_IDENTITY" "$1/$file"
			else
				codesign "$1/$file"
			fi
		elif [[ -f "$1/$file" ]]; then
			if [[ "$extension" == "dylib" ]]; then
        			/usr/bin/codesign --force --sign "$EXPANDED_CODE_SIGN_IDENTITY" "$1/$file"
        	fi
        fi
    done
}
#调用重签名方法
codesign "$BUILD_APP_PATH"
```
#### 中途可能遇到的问题
1. 这个问题是因为目标app的可执行文件没有可执行权限。(该问题已经在上面脚本中解决)
![](https://github.com/liliangde/Images/blob/main/逆向/install_error_1.png?raw=true)
2. 这个问题是因为我们签名用的授权文件中的bundle ID 和目标app的bundle ID 不一致，导致应用无法启动。(该问题已经在上面脚本中解决)
![](https://github.com/liliangde/Images/blob/main/逆向/install_error_2.png?raw=true)
3. 这个是因为工程设置的问题，解决：打开Xcode-->File-->Project Settings-->Build System 设置为Legacy Build System
![](https://github.com/liliangde/Images/blob/main/逆向/install_error_3.png?raw=true)

#### 思考
``Run Script``运行时机？

## 注入动态库
dyld（动态库加载器）在加载时会遍历``DYLD_INSERT_LIBRARIES``环境变量，加载对应的库。因此我们可以利用该环境变量注入自己的动态库，来实现hook目标应用的目的。（有关dyld加载流程，请读者自行查阅相关文章）
### 创建要注入的动态库
1. 在``NewAPP``工程下新建一个``macOS``-->``Library``的Target ``InsertedLib``
2. 修改``InsertedLib`` Target 的``Base SDK`` 为``iOS``
3. Build ``InsertedLib`` 
4. 将Products目录下的``libInsertedLib.dylib``文件拷贝到目标应用的``.app``目录下
5. 给``NewAPP``添加``DYLD_INSERT_LIBRARIES``环境变量 值为``@executable_path/libInsertedLib.dylib``
6. 在``InsertedLib`` Target 的``InsertedLib.m`` 文件中重写``+load()``方法，并下断点打印一句话
7. 运行``NewAPP``看断点是否停到第三步下断点的位置，如果停则说明注入成功

为了避免每次更新动态库文件后都要重新拷贝动态库文件到目标app中，故将上述步骤用shell实现。

```sh
cd ${SRCROOT}
xcodebuild -target InsertedLib -configuration Debug
cp -f "${SRCROOT}/build/Debug-iphoneos/libInsertedLib.dylib" "${SRCROOT}/zhenaiwang.app/libInsertedLib.dylib"
```

### 思考
要想让目标app执行我们注入的代码，除了重写``+load()``方法， 还有什么方式？
> ``__attribute__((constructor))``


## class-dump
### 说明
class-dump 是用来从可执行文件中获取类、方法、属性的工具

### 原理
![](https://github.com/liliangde/Images/blob/main/逆向/classDump.png?raw=true)

### 安装
> `` git clone https://github.com/nygard/class-dump.git ``

### 使用
1. 在解密后的目标app目录下找到``info.plist`` 中``Executable file``对应的MachO可执行文件
2. 进入MachO文件的同级目录，运行class-dump指令
> ``class-dump --arch arm64 zhenaiwang -H -o ../Headers ``

3. 进入目标app目录的同级目录，就可以看到``Headers``文件夹，里面包含了所有的头文件信息

## 符号化
### 为什么要符号化？
1. 不符号化的话在Xcode调试的时候，下断点只能通过地址来下，无法通过方法名来下断点，不方便调试
2. 看不到具体的调用堆栈信息
3. ...

### 符号化步骤
1. 下载符号化工具restore-symbol 
2. 查看目标可执行文件包含的架构类型，如果包含多个架构，就从中提取一个架构用来符号化。（如果只包含一个架构就忽略此步）
3. 将上一步得到的MachO文件符号化
4. 将符号化后的MachO文件替换原始的MachO文件

上述步骤的脚本如下 **（使用前先修改脚本中进入的MachO文件所在目录的哪一行代码）**：

```sh
# 安装restore-symbol工具
cd ~
# 判断是否安装过，如果没有安装过才下载安装
isInstall=$(ls -al | grep restore-symbol | wc -l) 
if (($isInstall==0));then 
git clone https://github.com/tobefuturer/restore-symbol.git
cd restore-symbol/
make
fi

#进入MachO文件所在目录，需要读者自行修改所在目录
cd ~/Desktop/逆向工程/NewAPP/zhenaiwang.app 

# 检查MachO文件包含的架构
isFat=$(lipo -info zhenaiwang | grep Non-fat | wc -l)
if (($isFat==0));then # 如果是Fat的，则提取其中的Arm64架构
lipo zhenaiwang -thin arm64 -output zhenaiwangArm64 &&
~/restore-symbol/restore-symbol zhenaiwangArm64 -o zhenaiwangSymbol
else
~/restore-symbol/restore-symbol zhenaiwang -o zhenaiwangSymbol
fi

# 用符号化后的MachO替换原有的MachO文件
cp -f zhenaiwangSymbol zhenaiwang

```

## LLDB动态调试
经过上面的操作，现在目标app已经成功的运行到我们的Xcode上面了，下面就可以对目标app进行调试了，首先需要了解一些LLDB动态调试的命令：

1. 查看模块在内存中加载的基地址
> ``image list -o -f ***``

2. 对指定的地址下断点
> ``breakpoint set -a ***``

3. 对指定的正则表达式下断点
> ``breakpoint set -r ***``

4. 给断点附加指令
> ``breakpoint command add *``

5. 断点时查看寄存器对应的值
> ``po $x0`` ``x/s $x1`` ``po $x2`` ``...``

## hook方法
经过上面一系列的操作我们已经成功的将目标app运行在我们的Xcode上面，并且已经成功的注入了自己的动态库。接下来我们就可以在我们新建的动态库中编写我们的hook代码了。

这里主要介绍``CaptainHook``的写法，先从github上面下载``CaptainHook``头文件然后拖入动态库目录下，并在``InsertedLib.m``中导入头文件，然后开始编写hook代码，步骤如下：

1. 使用``CHDeclareClass()``声明被hook方法所在的类
2. 使用``CHOptimizedMethod()`` hook目标函数
3. 使用``CHLoadLateClass()``在``CHConstructor``函数中注册第1步申明的类
4. 使用``CHHook()``在``CHConstructor``函数中注册第2步的hook函数
5. 使用``CHSuper()``在hook函数中调用原函数的实现

下面代码示范了如何hook ``AppDelegate`` 的 ``application:didFinishLaunchingWithOptions:``方法,然后在app启动的时候弹一个窗：

```objc
CHDeclareClass(ZAAppDelegate)

CHOptimizedMethod2(self, BOOL, ZAAppDelegate, application, UIApplication *, application, didFinishLaunchingWithOptions, NSDictionary *, launchOptions) {
    CHSuper2(ZAAppDelegate, application, application, didFinishLaunchingWithOptions, launchOptions);
    UIAlertController *alertVC = [UIAlertController alertControllerWithTitle:nil message:@"injectSuceess" preferredStyle:UIAlertControllerStyleAlert];
    UIAlertAction *action = [UIAlertAction actionWithTitle:@"cancel" style:UIAlertActionStyleCancel handler:nil];
    [alertVC addAction:action];
    [UIApplication.sharedApplication.keyWindow.rootViewController presentViewController:alertVC animated:YES completion:nil];
    return YES;
}

CHConstructor {
    CHLoadLateClass(ZAAppDelegate);
    CHHook2(ZAAppDelegate, application, didFinishLaunchingWithOptions);
}

```
