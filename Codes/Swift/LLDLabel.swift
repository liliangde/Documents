//
//  LLDLabel.swift
//  SMeet
//
//  Created by za on 2021/3/19.
//

import UIKit

class LLDLabel: UILabel {
    
    public var lineSpace: CGFloat?
    
    override var text: String? {
        didSet {
            if numberOfLines == 0 || numberOfLines > 1 {
                let paragraphStyle = NSMutableParagraphStyle()
                paragraphStyle.lineSpacing = lineSpace ?? defaultLineSpace()
                paragraphStyle.alignment = textAlignment
                paragraphStyle.lineBreakMode = lineBreakMode
                let attributes = [NSAttributedString.Key.paragraphStyle: paragraphStyle,
                                  NSAttributedString.Key.font: font ?? .systemFont(ofSize: 15),
                                  NSAttributedString.Key.foregroundColor: textColor ?? .black]
                attributedText = NSAttributedString(string: text ?? "", attributes: attributes)
            }
        }
    }
}

extension LLDLabel {
    private func defaultLineSpace() -> CGFloat {
        switch font.pointSize {
        case 12:
            return 3
        case 14:
            return 4
        case 15:
            return 5
        case 16:
            return 6
        case 18:
            return 8
        default:
            return 5
        }
    }
}
