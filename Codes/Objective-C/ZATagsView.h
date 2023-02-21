//
//  ZATagsView.h
//  zhenaiwang
//
//  Created by za on 2023/2/16.
//  Copyright © 2023 ZhenAiWang. All rights reserved.
//

#import <UIKit/UIKit.h>

NS_ASSUME_NONNULL_BEGIN

@interface ZATagsView : UIView

/// 计算标签视图的高度 （使用默认的配置）
/// - Parameters:
///   - tags: 字符串数组
///   - maxWidth: 最大宽度
+ (CGFloat)calHeightWithTags:(NSArray <NSString *> *)tags
                    maxWidth:(CGFloat)maxWidth;

/// 计算标签视图的高度 （使用默认的配置）
/// - Parameters:
///   - tags: 富文本数组
///   - maxWidth: 最大宽度
+ (CGFloat)calHeightWithAttrTags:(NSArray <NSAttributedString *> *)tags
                        maxWidth:(CGFloat)maxWidth;

/// 计算标签视图的高度
/// - Parameters:
///   - tags: 字符串数组
///   - maxWidth: 最大宽度
///   - font: 字体
///   - contentInsets: 标签内间距
///   - hSpace: 标签水平间距
///   - vSpace: 标签垂直间距
+ (CGFloat)calHeightWithTags:(NSArray <NSString *> *)tags
                    maxWidth:(CGFloat)maxWidth
                        font:(UIFont *)font
               contentInsets:(UIEdgeInsets)contentInsets
                      hSpace:(CGFloat)hSpace
                      vSpace:(CGFloat)vSpace;

/// 计算标签视图的高度
/// - Parameters:
///   - tags: 富文本数组
///   - maxWidth: 最大宽度
///   - contentInsets: 标签内间距
///   - hSpace: 标签水平间距
///   - vSpace: 标签垂直间距
+ (CGFloat)calHeightWithAttrTags:(NSArray <NSAttributedString *> *)tags
                        maxWidth:(CGFloat)maxWidth
                   contentInsets:(UIEdgeInsets)contentInsets
                          hSpace:(CGFloat)hSpace
                          vSpace:(CGFloat)vSpace;

/// 标签内间距（不设置默认UIEdgeInsetsMake(6, 8, 6, 8)）
@property (nonatomic, assign) UIEdgeInsets contentInsets;

/// 水平间距（不设置默认4）
@property (nonatomic, assign) CGFloat hSpace;

/// 垂直间距（不设置默认8）
@property (nonatomic, assign) CGFloat vSpace;

/// 标签背景色（不设置默认#F2F4F5）
@property (nonatomic, strong) UIColor *tagBgColor;

/// 标签字体颜色（不设置默认#2B2D33）
@property (nonatomic, strong) UIColor *titleColor;

/// 标签字体大小（不设置默认[UIFont systemFontOfSize:14]）
@property (nonatomic, strong) UIFont *titleFont;

/// 标签圆角（不设置默认8）
@property (nonatomic, assign) CGFloat cornerRadius;

/// 标签点击回调
@property (nonatomic, copy) void(^clickHandle)(NSInteger idx);

/// 刷新tags (刷新前必须有宽度)
/// - Parameter tags: 字符串数组
- (CGFloat)refresh:(NSArray <NSString *> *)tags;

/// 刷新tags (刷新前必须有宽度)
/// - Parameter tags: 富文本数组
- (CGFloat)refreshWithAttrTags:(NSArray <NSAttributedString *> *)tags;

@end

NS_ASSUME_NONNULL_END
