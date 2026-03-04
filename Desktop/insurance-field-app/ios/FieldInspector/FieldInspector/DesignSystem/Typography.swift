import SwiftUI

// MARK: - Deevo Sentinel Typography System
// Brand: Deevo Sentinel - Sovereign Claims Decision Infrastructure

public enum DeevoTypography {
    
    // MARK: - Display Styles (Headlines)
    
    /// Large display title - 34pt Bold
    public static let displayLarge = Font.system(size: 34, weight: .bold, design: .default)
    
    /// Medium display title - 28pt Bold
    public static let displayMedium = Font.system(size: 28, weight: .bold, design: .default)
    
    /// Small display title - 24pt Semibold
    public static let displaySmall = Font.system(size: 24, weight: .semibold, design: .default)
    
    // MARK: - Headline Styles
    
    /// Headline large - 20pt Semibold
    public static let headlineLarge = Font.system(size: 20, weight: .semibold, design: .default)
    
    /// Headline medium - 18pt Semibold
    public static let headlineMedium = Font.system(size: 18, weight: .semibold, design: .default)
    
    /// Headline small - 16pt Semibold
    public static let headlineSmall = Font.system(size: 16, weight: .semibold, design: .default)
    
    // MARK: - Body Styles
    
    /// Body large - 17pt Regular
    public static let bodyLarge = Font.system(size: 17, weight: .regular, design: .default)
    
    /// Body medium - 15pt Regular
    public static let bodyMedium = Font.system(size: 15, weight: .regular, design: .default)
    
    /// Body small - 13pt Regular
    public static let bodySmall = Font.system(size: 13, weight: .regular, design: .default)
    
    // MARK: - Label Styles
    
    /// Label large - 14pt Medium
    public static let labelLarge = Font.system(size: 14, weight: .medium, design: .default)
    
    /// Label medium - 12pt Medium
    public static let labelMedium = Font.system(size: 12, weight: .medium, design: .default)
    
    /// Label small - 11pt Medium
    public static let labelSmall = Font.system(size: 11, weight: .medium, design: .default)
    
    // MARK: - Caption Styles
    
    /// Caption - 12pt Regular
    public static let caption = Font.system(size: 12, weight: .regular, design: .default)
    
    /// Caption small - 10pt Regular
    public static let captionSmall = Font.system(size: 10, weight: .regular, design: .default)
    
    // MARK: - Monospace (for codes, IDs)
    
    /// Monospace medium - 14pt Monospaced
    public static let monoMedium = Font.system(size: 14, weight: .regular, design: .monospaced)
    
    /// Monospace small - 12pt Monospaced
    public static let monoSmall = Font.system(size: 12, weight: .regular, design: .monospaced)
}

// MARK: - Text Style Modifiers

extension View {
    /// Apply Deevo display large style
    func deevoDisplayLarge() -> some View {
        self.font(DeevoTypography.displayLarge)
            .foregroundColor(DeevoColors.textPrimary)
    }
    
    /// Apply Deevo display medium style
    func deevoDisplayMedium() -> some View {
        self.font(DeevoTypography.displayMedium)
            .foregroundColor(DeevoColors.textPrimary)
    }
    
    /// Apply Deevo headline large style
    func deevoHeadlineLarge() -> some View {
        self.font(DeevoTypography.headlineLarge)
            .foregroundColor(DeevoColors.textPrimary)
    }
    
    /// Apply Deevo headline medium style
    func deevoHeadlineMedium() -> some View {
        self.font(DeevoTypography.headlineMedium)
            .foregroundColor(DeevoColors.textPrimary)
    }
    
    /// Apply Deevo body large style
    func deevoBodyLarge() -> some View {
        self.font(DeevoTypography.bodyLarge)
            .foregroundColor(DeevoColors.textPrimary)
    }
    
    /// Apply Deevo body medium style
    func deevoBodyMedium() -> some View {
        self.font(DeevoTypography.bodyMedium)
            .foregroundColor(DeevoColors.textSecondary)
    }
    
    /// Apply Deevo label style
    func deevoLabel() -> some View {
        self.font(DeevoTypography.labelMedium)
            .foregroundColor(DeevoColors.textSecondary)
    }
    
    /// Apply Deevo caption style
    func deevoCaption() -> some View {
        self.font(DeevoTypography.caption)
            .foregroundColor(DeevoColors.textTertiary)
    }
}

// MARK: - Text Styles Enum (for dynamic styling)

public enum DeevoTextStyle {
    case displayLarge
    case displayMedium
    case displaySmall
    case headlineLarge
    case headlineMedium
    case headlineSmall
    case bodyLarge
    case bodyMedium
    case bodySmall
    case labelLarge
    case labelMedium
    case labelSmall
    case caption
    case captionSmall
    case monoMedium
    case monoSmall
    
    var font: Font {
        switch self {
        case .displayLarge: return DeevoTypography.displayLarge
        case .displayMedium: return DeevoTypography.displayMedium
        case .displaySmall: return DeevoTypography.displaySmall
        case .headlineLarge: return DeevoTypography.headlineLarge
        case .headlineMedium: return DeevoTypography.headlineMedium
        case .headlineSmall: return DeevoTypography.headlineSmall
        case .bodyLarge: return DeevoTypography.bodyLarge
        case .bodyMedium: return DeevoTypography.bodyMedium
        case .bodySmall: return DeevoTypography.bodySmall
        case .labelLarge: return DeevoTypography.labelLarge
        case .labelMedium: return DeevoTypography.labelMedium
        case .labelSmall: return DeevoTypography.labelSmall
        case .caption: return DeevoTypography.caption
        case .captionSmall: return DeevoTypography.captionSmall
        case .monoMedium: return DeevoTypography.monoMedium
        case .monoSmall: return DeevoTypography.monoSmall
        }
    }
}
