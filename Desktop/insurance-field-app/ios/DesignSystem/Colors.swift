import SwiftUI

// MARK: - Deevo Sentinel Design System Colors
// Brand: Deevo Sentinel - Sovereign Claims Decision Infrastructure
// Powered by Deevo Analytics

public enum DeevoColors {
    // MARK: - Primary Palette
    
    /// Deep Navy - Primary brand color
    /// Hex: #0B1F3A
    public static let primary = Color(red: 11/255, green: 31/255, blue: 58/255)
    
    /// Secondary Blue
    /// Hex: #1F3C88
    public static let secondary = Color(red: 31/255, green: 60/255, blue: 136/255)
    
    /// Soft Gold - Accent color for highlights and CTAs
    /// Hex: #C9A227
    public static let accent = Color(red: 201/255, green: 162/255, blue: 39/255)
    
    /// Light Gold - Lighter accent for gradients
    /// Hex: #E0C060
    public static let accentLight = Color(red: 224/255, green: 192/255, blue: 96/255)
    
    /// Error Red - For destructive actions and error states
    /// Hex: #8B1E1E
    public static let error = Color(red: 139/255, green: 30/255, blue: 30/255)
    
    /// Background Dark - Main dark background
    /// Hex: #121417
    public static let backgroundDark = Color(red: 18/255, green: 20/255, blue: 23/255)
    
    // MARK: - Extended Palette
    
    /// Surface color for cards and elevated elements
    public static let surface = Color(red: 24/255, green: 28/255, blue: 35/255)
    
    /// Surface elevated - slightly lighter for layered UI
    public static let surfaceElevated = Color(red: 32/255, green: 38/255, blue: 48/255)
    
    /// Border color for subtle separators
    public static let border = Color(red: 45/255, green: 52/255, blue: 65/255)
    
    /// Divider color (alias for border)
    public static let divider = Color(red: 45/255, green: 52/255, blue: 65/255)
    
    /// Text primary - main text color
    public static let textPrimary = Color.white
    
    /// Text secondary - subdued text
    public static let textSecondary = Color(red: 156/255, green: 163/255, blue: 175/255)
    
    /// Text tertiary - very subdued text
    public static let textTertiary = Color(red: 107/255, green: 114/255, blue: 128/255)
    
    // MARK: - Status Colors
    
    /// Success green
    public static let success = Color(red: 34/255, green: 139/255, blue: 34/255)
    
    /// Warning amber
    public static let warning = Color(red: 217/255, green: 164/255, blue: 32/255)
    
    /// Info blue
    public static let info = Color(red: 59/255, green: 130/255, blue: 246/255)
    
    // MARK: - Risk Band Colors
    
    /// Low risk - Green
    public static let riskLow = Color(red: 34/255, green: 139/255, blue: 34/255)
    
    /// Moderate risk - Yellow
    public static let riskModerate = Color(red: 217/255, green: 164/255, blue: 32/255)
    
    /// Elevated risk - Orange
    public static let riskElevated = Color(red: 234/255, green: 88/255, blue: 12/255)
    
    /// Critical risk - Red
    public static let riskCritical = Color(red: 185/255, green: 28/255, blue: 28/255)
}

// MARK: - Color Extensions

extension Color {
    /// Deevo Sentinel primary color
    static var deevoPrimary: Color { DeevoColors.primary }
    
    /// Deevo Sentinel secondary color
    static var deevoSecondary: Color { DeevoColors.secondary }
    
    /// Deevo Sentinel accent color
    static var deevoAccent: Color { DeevoColors.accent }
    
    /// Deevo Sentinel error color
    static var deevoError: Color { DeevoColors.error }
    
    /// Deevo Sentinel background
    static var deevoBackground: Color { DeevoColors.backgroundDark }
}

// MARK: - UIColor Extensions (for UIKit interop)

extension UIColor {
    static var deevoPrimary: UIColor {
        UIColor(red: 11/255, green: 31/255, blue: 58/255, alpha: 1)
    }
    
    static var deevoSecondary: UIColor {
        UIColor(red: 31/255, green: 60/255, blue: 136/255, alpha: 1)
    }
    
    static var deevoAccent: UIColor {
        UIColor(red: 201/255, green: 162/255, blue: 39/255, alpha: 1)
    }
    
    static var deevoError: UIColor {
        UIColor(red: 139/255, green: 30/255, blue: 30/255, alpha: 1)
    }
    
    static var deevoBackgroundDark: UIColor {
        UIColor(red: 18/255, green: 20/255, blue: 23/255, alpha: 1)
    }
}
