# iOS非越狱逆向神器-MonkeyDev
## MonkeyDev简介
原有iOSOpenDev的升级，<mark>非越狱</mark>插件开发集成神器！

* 可以使用Xcode开发CaptainHook Tweak、Logos Tweak 和 Command-line Tool，在越狱机器开发插件。
* <mark>只需拖入一个砸壳应用，自动集成class-dump、restore-symbol、Reveal、Cycript和注入的动态库并重签名安装到非越狱机器。
* 支持调试自己编写的动态库和第三方App
* 支持通过CocoaPods第三方应用集成SDK以及非越狱插件，简单来说就是通过CocoaPods搭建了一个非越狱插件商店。

## MonkeyDev安装
### 准备工作
1. Homebrew(macOS 缺失的软件包的管理器)安装

	```
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	```
2. 安装最新的[theos](https://github.com/theos/theos/wiki/Installation-macOS)
	
	```
	sudo git clone --recursive https://github.com/theos/theos.git /opt/theos
	```
3. 安装ldid
	
	```
	brew install ldid
	```

### 开始安装MonkeyDev

1. 选择指定的Xcode进行安装,<mark>Xcode.app</mark>为电脑上安装的Xcode

	```
	sudo xcode-select -s /Applications/Xcode.app
	```
2. 执行安装命令

	```
	sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/AloneMonkey/MonkeyDev/master/bin/md-install)"
	```
	
#### 重启Xcode 新建工程滚到最下面，不出意外你将看到如下界面
![](MonkeyDev.png)
#### 恭喜你安装成功了

### MonkeyDev卸载及更新
#### 卸载
```
sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/AloneMonkey/MonkeyDev/master/bin/md-uninstall)"
```

#### 更新
```
sudo /bin/sh -c "$(curl -fsSL https://raw.githubusercontent.com/AloneMonkey/MonkeyDev/master/bin/md-update)"
```

## 实践：微信自动抢红包

1. 从pp助手下载砸壳后的微信应用，<mark>注意：不要连接任何手机至电脑，不然无法下载</mark>
	![](pp_weichat_download.png)
2. 打开Xcode 新建工程，选择刚刚安装的MonkeyDev目录下的MonkeyAPP
	![](weichat_app.png)
3. 新建工程后你将得到如下目录的工程
	![](weichat_drap_app.png)
4. 恭喜，已成功逆向，赶紧跑起来试试啊，command+R

### Duang～
![](weichat_crash.png)

别慌，接着command+R
![](weichat_Home.png)

恭喜您成功逆向了微信

### class-dump 出微信的所有头文件

1. MonkeyAPP 已经集成了class-dump 直接在Build Settings 里面滚到最下面设置即可
	![](weichat_buildSetting.png)
	
2. commend+B 将会在工程目录下生成微信头文件的目录，如下图
	![](weichat_Headers.png)

### 自动抢红包原理
1. hook微信接收消息的方法

	```objc
	- (void)AsyncOnAddMsg:(id)arg1 MsgWrap:(id)arg2;
	```
2. 在接受消息的方法判断该消息是否是红包消息
3. 如果是红包消息则手动请求后台接口获取该红包的完整信息

	```objc
	((void (*)(id, SEL, NSMutableDictionary*))objc_msgSend)(logicMgr, @selector(ReceiverQueryRedEnvelopesRequest:), dictParam);
	```
4. hook请求红包完整信息的响应回调 

	```objc
	- (void)OnWCToHongbaoCommonResponse:(id)arg1 Request:(id)arg2;
	```
5. 在响应回调中请求后台打开该红包

	```objc
	((void (*)(id, SEL, NSMutableDictionary*))objc_msgSend)(logicMgr, @selector(OpenRedEnvelopesRequest:), params);
	```

### Hook 微信方法的调用

#### 了解CaptainHook基本用法
* 申明需要hook的类

	```objc
	CHDeclareClass(CMessageMgr)
	```
* 申明需要hook的方法

	```objc
	CHOptimizedMethod2(self, void, CMessageMgr, AsyncOnAddMsg, id, arg1, MsgWrap, id, arg2)
	```
* 调用原来方法的实现

	```objc
	CHSuper2(CMessageMgr, AsyncOnAddMsg, arg1, MsgWrap, arg2);
	```

* 装载所有需要hook的类和方法

	```objc
	CHConstructor {
	    CHLoadLateClass(CMessageMgr);
	    CHClassHook2(CMessageMgr, AsyncOnAddMsg, MsgWrap);
	}
	```
* 加载需要被hook的类

	```objc
	CHLoadLateClass(CMessageMgr);
	```
* 加载需要被hook的方法

	```objc
	CHClassHook2(CMessageMgr, AsyncOnAddMsg, MsgWrap);
	```
	
### 自动抢红包完整代码
1. 找到新建项目中的WeiChatDylib.h文件，然后在文件的末尾添加如下代码

	```objc
	@interface CMessageMgr
	
	- (void)AsyncOnAddMsg:(id)arg1 MsgWrap:(id)arg2;
	
	@end
	
	@interface SKBuiltinBuffer_t
	
	@property(retain, nonatomic) NSData *buffer; // @dynamic buffer
	
	@end
	
	@interface WCRedEnvelopesLogicMgr : NSObject
	
	- (void)OnWCToHongbaoCommonResponse:(id)arg1 Request:(id)arg2;
	- (void)ReceiverQueryRedEnvelopesRequest:(id)arg1;
	- (void)OpenRedEnvelopesRequest:(id)arg1;
	
	@property(nonatomic) int cgiCmdid; // @dynamic cgiCmdid;
	@property(retain, nonatomic) NSString *errorMsg; // @dynamic errorMsg;
	@property(nonatomic) int errorType; // @dynamic errorType;
	@property(retain, nonatomic) NSString *platMsg; // @dynamic platMsg;
	@property(nonatomic) int platRet; // @dynamic platRet;
	@property(retain, nonatomic) SKBuiltinBuffer_t *retText; // @dynamic retText;
	
	@end
	
	@interface MMServiceCenter : NSObject
	
	+ (id)defaultCenter;
	- (id)getService:(Class)Class;
	
	@end
	
	@interface CMessageWrap : NSObject
	
	@property(nonatomic) unsigned int m_uiMessageType; // @synthesize m_uiMessageType;
	@property(retain, nonatomic) NSString *m_nsFromUsr; // @synthesize m_nsFromUsr;
	@property(retain, nonatomic) NSString *m_nsContent; // @synthesize m_nsContent;
	
	@end
	
	@interface CBaseContact : NSObject
	
	@property(retain, nonatomic) NSString *m_nsUsrName; // @synthesize m_nsUsrName;
	@property(retain, nonatomic) NSString *m_nsHeadImgUrl; // @synthesize m_nsHeadImgUrl;
	
	- (id)getContactDisplayName;
	
	@end
	
	@interface CContactMgr : NSObject
	
	- (id)getSelfContact;
	
	@end
	```
2. 找到新建项目中的WeiChatDylib.m文件，然后在文件的末尾添加如下代码
	
	```objc
	CHDeclareClass(CMessageMgr)
	CHOptimizedMethod2(self, void, CMessageMgr, AsyncOnAddMsg, id, arg1, MsgWrap, id, arg2) {
	    CHSuper(2, CMessageMgr, AsyncOnAddMsg, arg1, MsgWrap, arg2);
	    
	    NSUInteger m_uiMessageType = [arg2 m_uiMessageType];
	    
	    id m_nsFromUsr = [arg2 m_nsFromUsr];
	    id m_nsContent = [arg2 m_nsContent];
	    
	    switch(m_uiMessageType) {
	        case 49: {
	            id logicMgr = [[objc_getClass("MMServiceCenter") defaultCenter] getService:objc_getClass("WCRedEnvelopesLogicMgr")];
	            id contactManager =[[objc_getClass("MMServiceCenter") defaultCenter] getService:objc_getClass("CContactMgr")];
	            id selfContact = [contactManager getSelfContact];
	            id m_nsUsrName = [selfContact m_nsUsrName];
	            
	            if ([m_nsFromUsr isEqualToString:m_nsUsrName]) {//不抢自己的红包
	                return;
	            }
	            
	            if ([m_nsContent rangeOfString:@"wxpay://"].location != NSNotFound) {
	                
	                NSString *nativeUrl = m_nsContent;
	                NSRange rangeStart = [m_nsContent rangeOfString:@"wxpay://c2cbizmessagehandler/hongbao"];
	                if (rangeStart.location != NSNotFound) {
	                    NSUInteger locationStart = rangeStart.location;
	                    nativeUrl = [nativeUrl substringFromIndex:locationStart];
	                }
	                
	                NSRange rangeEnd = [nativeUrl rangeOfString:@"]]"];
	                if (rangeEnd.location != NSNotFound) {
	                    NSUInteger locationEnd = rangeEnd.location;
	                    nativeUrl = [nativeUrl substringToIndex:locationEnd];
	                }
	                
	                NSString *naUrl = [nativeUrl substringFromIndex:[@"wxpay://c2cbizmessagehandler/hongbao/receivehongbao?" length]];
	                
	                NSArray *parameterPairs =[naUrl componentsSeparatedByString:@"&"];
	                
	                NSMutableDictionary *parameters = [NSMutableDictionary dictionaryWithCapacity:[parameterPairs count]];
	                for (NSString *currentPair in parameterPairs) {
	                    NSRange range = [currentPair rangeOfString:@"="];
	                    if(range.location == NSNotFound)
	                        continue;
	                    NSString *key = [currentPair substringToIndex:range.location];
	                    NSString *value =[currentPair substringFromIndex:range.location + 1];
	                    [parameters setObject:value forKey:key];
	                }
	                
	                //红包参数
	                NSMutableDictionary *params = [@{} mutableCopy];
	
	                [params setObject:parameters[@"msgtype"] forKey:@"msgType"];
	                [params setObject:parameters[@"sendid"] forKey:@"sendId"];
	                [params setObject:parameters[@"channelid"] forKey:@"channelId"];
	
	                id getContactDisplayName = [selfContact getContactDisplayName];
	                id m_nsHeadImgUrl = [selfContact m_nsHeadImgUrl];
	
	                [params setObject:getContactDisplayName forKey:@"nickName"];
	                [params setObject:m_nsHeadImgUrl forKey:@"headImg"];
	                [params setObject:[NSString stringWithFormat:@"%@", nativeUrl] forKey:@"nativeUrl"];
	                [params setObject:m_nsFromUsr forKey:@"sessionUserName"];
	
	                [[NSUserDefaults standardUserDefaults] setObject:params forKey:@"ZTParamKey"];
	                
	                NSMutableDictionary* dictParam = [NSMutableDictionary dictionary];
	                
	                [dictParam setObject:@"0" forKey:@"agreeDuty"];                                             //agreeDuty
	                [dictParam setObject:parameters[@"channelid"] forKey:@"channelId"];        //channelId
	                [dictParam setObject:@"1" forKey:@"inWay"];                                                 //inWay
	                [dictParam setObject:parameters[@"msgtype"] forKey:@"msgType"];            //msgType
	                [dictParam setObject:nativeUrl forKey:@"nativeUrl"];                                     //nativeUrl
	                [dictParam setObject:parameters[@"sendid"] forKey:@"sendId"];              //sendId
	                
	                NSLog(@"dictParam=%@", dictParam);
	                ((void (*)(id, SEL, NSMutableDictionary*))objc_msgSend)(logicMgr, @selector(ReceiverQueryRedEnvelopesRequest:), dictParam);
	                
	                return;
	            }
	            
	            break;
	        }
	        default:
	            break;
	    }
	}
	
	CHDeclareClass(WCRedEnvelopesLogicMgr);
	CHOptimizedMethod2(self, void, WCRedEnvelopesLogicMgr, OnWCToHongbaoCommonResponse, id, arg1, Request, id, arg2) {
	    
	    CHSuper2(WCRedEnvelopesLogicMgr, OnWCToHongbaoCommonResponse, arg1, Request, arg2);
	    
	    if ([NSStringFromClass([arg1 class]) isEqualToString:@"HongBaoRes"]) {
	        NSData *data = [[arg1 retText] buffer];
	        
	        if (nil != data && 0 < [data length]) {
	            NSError* error = nil;
	            id jsonObj = [NSJSONSerialization JSONObjectWithData:data
	                                                         options:NSJSONReadingAllowFragments
	                                                           error:&error];
	            if (nil != error) {
	                NSLog(@"error %@", [error localizedDescription]);
	            } else if (nil != jsonObj) {
	                if ([NSJSONSerialization isValidJSONObject:jsonObj]) {
	                    if ([jsonObj isKindOfClass:[NSDictionary class]]) {
	                        id idTemp = jsonObj[@"timingIdentifier"];
	                        if (idTemp) {
	                            NSMutableDictionary *params = [[[NSUserDefaults standardUserDefaults] objectForKey:@"ZTParamKey"] mutableCopy];
	                            [[NSUserDefaults standardUserDefaults] setObject:[NSMutableDictionary dictionary] forKey:@"ZTParamKey"];
	                            [params setObject:idTemp forKey:@"timingIdentifier"]; // "timingIdentifier"字段
	                            
	                            // 防止重复请求
	                            if (params.allKeys.count < 2) {
	                                return;
	                            }
	                            
	                            id logicMgr = [[objc_getClass("MMServiceCenter") defaultCenter] getService:objc_getClass("WCRedEnvelopesLogicMgr")];
	                            
	                            dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(1 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
	                                ((void (*)(id, SEL, NSMutableDictionary*))objc_msgSend)(logicMgr, @selector(OpenRedEnvelopesRequest:), params);
	                            });
	                        }
	                    }
	                }
	            }
	        }
	    }
	}
	
	CHConstructor {
	    CHLoadLateClass(CMessageMgr);
	    CHLoadLateClass(WCRedEnvelopesLogicMgr);
	    CHClassHook2(CMessageMgr, AsyncOnAddMsg, MsgWrap);
	    CHClassHook2(WCRedEnvelopesLogicMgr, OnWCToHongbaoCommonResponse, Request);
	}
	```
	
3. command + R 试试效果
![](auto_qianghongbao.MP4)