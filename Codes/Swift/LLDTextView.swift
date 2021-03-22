//
//  LLDTextView.swift
//  SMeet
//
//  Created by za on 2021/3/5.
//

import UIKit

class LLDTextView: UITextView {
    
    // MARK: - Public
    
    /// textView 最大高度
    public var maxHeight: CGFloat?
    
    /// textView 最小高度
    public var minHeight: CGFloat?
    
    /// 高度变更回调
    public var heightDidChange:((_ height: CGFloat) -> Void)?
    
    /// 占位富文本
    public var attributedPlaceholder: NSAttributedString? {
        didSet {
            placeholderTextView.attributedText = attributedPlaceholder
        }
    }
    
    /// 占位颜色
    public var placeholderColor: UIColor? {
        didSet {
            placeholderTextView.textColor = placeholderColor
        }
    }
    
    /// 占位字体大小
    public var placeholderFont: UIFont? {
        didSet {
            placeholderTextView.font = placeholderFont
        }
    }
    
    /// 占位文本
    public var placeholder: String? {
        didSet {
            placeholderTextView.text = placeholder
        }
    }
    
    override var textContainerInset: UIEdgeInsets {
        didSet {
            placeholderTextView.textContainerInset = textContainerInset
        }
    }
    
    override var backgroundColor: UIColor? {
        didSet {
            placeholderTextView.backgroundColor = backgroundColor
        }
    }
    
    override var text: String! {
        didSet {
            textDidChange(nil)
        }
    }
    
    /// 更新textView文本
    /// - Parameters:
    ///   - text: 要更新的文本
    ///   - clear: 是否覆盖当前文本
    public func refresh(text: String, clear: Bool = false) {
        if clear {
            self.text = text
        } else {
            if let curText = self.text {
                let location = selectedRange.location
                let front = String(curText.prefix(location))
                let tail = String(curText.suffix(curText.count - location))
                self.text = front + text + tail
                self.selectedRange = NSMakeRange(location + text.count, 0)
            }
        }
        
        textDidChange(nil)
    }
    
    public var lineSpace: CGFloat? {
        didSet {
            let paragraphStyle = NSMutableParagraphStyle()
            paragraphStyle.lineSpacing = lineSpace ?? 5
            typingAttributes = [.paragraphStyle: paragraphStyle,
                                .font: font ?? .systemFont(ofSize: 15),
                                .foregroundColor: textColor ?? .black]
        }
    }
    
    // MARK: - Private Properties
    
    /// 记录之前的文本高度
    private var oldContainerViewHeight: CGFloat = 0
    
    /// 当前文本高度
    private var containerViewHeight: CGFloat {
        get {
            for view in subviews {
                if let cls = NSClassFromString("_" + "UIText" + "ContainerView"),
                   view.isKind(of: cls) {
                    return view.bounds.height
                }
            }
            
            return bounds.height
        }
    }
    
    // MARK: - Event
    @objc func textDidChange(_: Notification?) {
        placeholderTextView.layer.isHidden = (text.count > 0)
        
        if oldContainerViewHeight != containerViewHeight {
            oldContainerViewHeight = containerViewHeight
            
            if let maxHeight = maxHeight,
               oldContainerViewHeight > maxHeight {
                heightDidChange?(maxHeight)
            } else if let minHeight = minHeight,
                      oldContainerViewHeight < minHeight {
                heightDidChange?(minHeight)
            } else {
                heightDidChange?(oldContainerViewHeight)
            }
        }
    }
    
    // MARK: - Init
    override init(frame: CGRect, textContainer: NSTextContainer?) {
        super.init(frame: frame, textContainer: textContainer)
        
        insertSubview(placeholderTextView, at: 0)
        NotificationCenter.default.addObserver(self, selector: #selector(textDidChange(_:)), name: UITextView.textDidChangeNotification, object: self)
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        placeholderTextView.frame = bounds
    }
    
    // MARK: - Private
    private let placeholderTextView: UITextView = {
        let textView = UITextView(frame: CGRect.zero)
        textView.isUserInteractionEnabled = false
        textView.showsVerticalScrollIndicator = false
        textView.showsHorizontalScrollIndicator = false
        return textView
    }()
}
