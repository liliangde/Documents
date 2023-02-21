//
//  ZATagsView.m
//  zhenaiwang
//
//  Created by za on 2023/2/16.
//  Copyright © 2023 ZhenAiWang. All rights reserved.
//

#import "ZATagsView.h"

@interface ZATagItemView : UIView
@property (nonatomic, strong) UILabel *textLabel;
@end

@implementation ZATagItemView

- (instancetype)initWithFrame:(CGRect)frame {
    if (self = [super initWithFrame:frame]) {
        [self setupUI];
    }
    return self;
}

#pragma mark - Private Methods

- (void)setupUI {
    [self addSubview:self.textLabel];
}

#pragma mark - Setter or Getter

- (UILabel *)textLabel {
    if (!_textLabel) {
        _textLabel = [[UILabel alloc] initWithFrame:CGRectZero];
        _textLabel.numberOfLines = 0;
    }
    return _textLabel;
}

@end

@interface ZATagsView ()

@property (nonatomic, assign) CGFloat maxWidth;

@property (nonatomic, strong) NSMutableArray <ZATagItemView *> *tagItemViews;

@property (nonatomic, copy) NSArray *lastShowTags;

@property (nonatomic, strong) NSMutableDictionary *contentSizeCache;

@property (nonatomic, assign) NSTimeInterval lastRespondClickHandleTime;

@end

@implementation ZATagsView

+ (CGFloat)calHeightWithTags:(NSArray <NSString *> *)tags
                    maxWidth:(CGFloat)maxWidth {
    return [self calHeightWithTags:tags maxWidth:maxWidth font:[self defaultFont] contentInsets:[self defaultContentInsets] hSpace:[self defaultHspace] vSpace:[self defaultVspace]];
}

+ (CGFloat)calHeightWithAttrTags:(NSArray <NSAttributedString *> *)tags
                        maxWidth:(CGFloat)maxWidth {
    return [self calHeightWithAttrTags:tags maxWidth:maxWidth contentInsets:[self defaultContentInsets] hSpace:[self defaultHspace] vSpace:[self defaultVspace]];
}

+ (CGFloat)calHeightWithTags:(NSArray <NSString *> *)tags
                    maxWidth:(CGFloat)maxWidth
                        font:(UIFont *)font
               contentInsets:(UIEdgeInsets)contentInsets
                      hSpace:(CGFloat)hSpace
                      vSpace:(CGFloat)vSpace {
    NSMutableArray *attrs = [NSMutableArray arrayWithCapacity:tags.count];
    for (int i = 0; i < tags.count; i++) {
        NSAttributedString *content = [[NSAttributedString alloc] initWithString:tags[i] attributes:@{NSFontAttributeName: font}];
        [attrs addObject:content];
    }
    return [self calHeightWithAttrTags:attrs maxWidth:maxWidth contentInsets:contentInsets hSpace:hSpace vSpace:vSpace];
}

+ (CGFloat)calHeightWithAttrTags:(NSArray <NSAttributedString *> *)tags
                        maxWidth:(CGFloat)maxWidth
                   contentInsets:(UIEdgeInsets)contentInsets
                          hSpace:(CGFloat)hSpace
                          vSpace:(CGFloat)vSpace {
    ZATagsView *tagsView = [[ZATagsView alloc] initWithFrame:CGRectMake(0, 0, maxWidth, 0)];
    tagsView.contentInsets = contentInsets;
    tagsView.hSpace = hSpace;
    tagsView.vSpace = vSpace;
    return [tagsView refreshWithAttrTags:tags];
}

- (instancetype)initWithFrame:(CGRect)frame {
    if (self = [super initWithFrame:frame]) {
        self.maxWidth = frame.size.width;
        self.hSpace = [ZATagsView defaultHspace];
        self.vSpace = [ZATagsView defaultVspace];
        self.titleFont = [ZATagsView defaultFont];
        self.contentInsets = [ZATagsView defaultContentInsets];
        self.cornerRadius = 8;
        self.tagBgColor = [UIColor colorWithHexString:@"#F2F4F5"];
        self.titleColor = [UIColor colorWithHexString:@"#2B2D33"];
    }
    return self;
}

- (CGFloat)refresh:(NSArray <NSString *> *)tags {
    NSMutableArray *attrs = [NSMutableArray arrayWithCapacity:tags.count];
    for (int i = 0; i < tags.count; i++) {
        NSAttributedString *content = [[NSAttributedString alloc] initWithString:tags[i] attributes:@{NSForegroundColorAttributeName: self.titleColor, NSFontAttributeName: self.titleFont}];
        [attrs addObject:content];
    }
    return [self refreshWithAttrTags:attrs];
}

- (CGFloat)refreshWithAttrTags:(NSArray <NSAttributedString *> *)tags {
    // 如果当前展示的和将要展示的是一样的就直接返回
    if ([self.lastShowTags isEqualToArray:tags]) {
        return [self totalHeight];
    }
    
    self.lastShowTags = tags;
    
    // 如果将要展示的tag比现有的还多，则新建taglabel
    if (self.tagItemViews.count < tags.count) {
        for (NSUInteger i = self.tagItemViews.count; i < tags.count; i++) {
            ZATagItemView *itemView = [[ZATagItemView alloc] initWithFrame:CGRectZero];
            itemView.tag = i;
            itemView.backgroundColor = self.tagBgColor;
            itemView.layer.cornerRadius = self.cornerRadius;
            
            [self addSubview:itemView];
            [self.tagItemViews addObject:itemView];
        }
    }
    
    CGFloat left = 0;
    CGFloat top = 0;
    for (int i = 0; i < self.tagItemViews.count; i++) {
        ZATagItemView *itemView = self.tagItemViews[i];
        itemView.hidden = (i >= tags.count);
        
        if (i < tags.count) {
            NSAttributedString *content = tags[i];
            itemView.textLabel.attributedText = content;
            
            NSArray *result = [self calContentSize:content left:left];
            CGSize contentSize = [result.firstObject CGSizeValue];
            CGFloat itemWidth = [result[1] floatValue];
            CGFloat itemHeight = [result.lastObject floatValue];
            
            BOOL isReturn = contentSize.height > self.titleFont.lineHeight * 1.5; // 是否换行
            
            // 如果文案换行了 说明当前行放不下了 要换行
            if (isReturn) {
                left = 0;
                NSInteger lastTagIdx = i - 1;
                if (lastTagIdx < self.tagItemViews.count) {
                    top = (self.tagItemViews[lastTagIdx].bottom + self.vSpace);
                }
                
                // 换行重新计算文本大小 因为宽度变了
                NSArray *result = [self calContentSize:content left:left];
                contentSize = [result.firstObject CGSizeValue];
                itemWidth = [result[1] floatValue];
                itemHeight = [result.lastObject floatValue];
            }
            
            itemView.frame = CGRectMake(left, top, itemWidth, itemHeight);
            itemView.textLabel.frame = CGRectMake(self.contentInsets.left, self.contentInsets.top, contentSize.width, contentSize.height);
            
            left += (itemView.width + self.hSpace);
        }
    }
    self.height = [self totalHeight];
    
    return self.height;
}

#pragma mark - Private Methods

- (UIView *)hitTest:(CGPoint)point withEvent:(UIEvent *)event {
    for (UIView *itemView in self.subviews) {
        if (CGRectContainsPoint(itemView.frame, point) && self.clickHandle) {
            // 解决 hitTest方法会回调两次的问题
            if (self.lastRespondClickHandleTime != event.timestamp) {
                self.lastRespondClickHandleTime = event.timestamp;
                self.clickHandle(itemView.tag);
                return itemView;
            }
            break;
        }
    }
    return [super hitTest:point withEvent:event];
}

- (NSArray *)calContentSize:(NSAttributedString *)content left:(CGFloat)left {
    // 先取缓存避免重复计算
    NSString *key = [NSString stringWithFormat:@"%f-%@",left, content.description];
    NSArray *result = self.contentSizeCache[key];
    if (result == nil) {
        // maxWidth 有可能是负值，所以最终计算的时候可以给1计算高度
        CGFloat maxWidth = self.maxWidth - left - self.contentInsets.left - self.contentInsets.right;
        
        CGSize contentSize = [content boundingRectWithSize:CGSizeMake(MAX(maxWidth, 1), CGFLOAT_MAX) options:NSStringDrawingUsesLineFragmentOrigin | NSStringDrawingUsesFontLeading  context:nil].size;
        CGFloat itemWidth = contentSize.width + self.contentInsets.left + self.contentInsets.right;
        CGFloat itemHeight = contentSize.height + self.contentInsets.top + self.contentInsets.bottom;
        
        self.contentSizeCache[key] = result;
        result = @[@(contentSize), @(itemWidth), @(itemHeight)];
    }
    return result;
}

- (CGFloat)totalHeight {
    CGFloat height = 0;
    // 找到最后一个没有隐藏的子视图
    for (UIView *itemView in self.tagItemViews) {
        if (!itemView.hidden) {
            height = itemView.bottom;
        } else {
            break;
        }
    }
    return height;
}

#pragma mark - Setter or Getter

+ (UIFont *)defaultFont {
    return [UIFont systemFontOfSize:14];
}

+ (CGFloat)defaultVspace {
    return 8;
}

+ (CGFloat)defaultHspace {
    return 4;
}

+ (UIEdgeInsets)defaultContentInsets {
    return UIEdgeInsetsMake(6, 8, 6, 8);
}

- (void)setFrame:(CGRect)frame {
    self.maxWidth = frame.size.width;
    [super setFrame:frame];
}

- (NSMutableArray *)tagItemViews {
    if (!_tagItemViews) {
        _tagItemViews = [NSMutableArray array];
    }
    return _tagItemViews;
}

- (NSMutableDictionary *)contentSizeCache {
    if (!_contentSizeCache) {
        _contentSizeCache = [NSMutableDictionary dictionary];
    }
    return _contentSizeCache;
}

@end
