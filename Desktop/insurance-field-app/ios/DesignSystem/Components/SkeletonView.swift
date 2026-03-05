import SwiftUI

// MARK: - Deevo Sentinel Skeleton View
// Executive loading states for professional appearance

public struct SkeletonView: View {
    let width: CGFloat?
    let height: CGFloat
    let cornerRadius: CGFloat
    
    @State private var isAnimating = false
    
    public init(
        width: CGFloat? = nil,
        height: CGFloat = 20,
        cornerRadius: CGFloat = 6
    ) {
        self.width = width
        self.height = height
        self.cornerRadius = cornerRadius
    }
    
    public var body: some View {
        RoundedRectangle(cornerRadius: cornerRadius)
            .fill(
                LinearGradient(
                    gradient: Gradient(colors: [
                        DeevoColors.surface,
                        DeevoColors.surfaceElevated,
                        DeevoColors.surface
                    ]),
                    startPoint: isAnimating ? .leading : .trailing,
                    endPoint: isAnimating ? .trailing : .leading
                )
            )
            .frame(width: width, height: height)
            .onAppear {
                withAnimation(
                    Animation.easeInOut(duration: 1.5)
                        .repeatForever(autoreverses: true)
                ) {
                    isAnimating = true
                }
            }
    }
}

// MARK: - Skeleton Card

public struct SkeletonCard: View {
    public init() {}
    
    public var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                SkeletonView(width: 50, height: 50, cornerRadius: 10)
                VStack(alignment: .leading, spacing: 8) {
                    SkeletonView(width: 150, height: 16)
                    SkeletonView(width: 100, height: 12)
                }
                Spacer()
                SkeletonView(width: 70, height: 24, cornerRadius: 12)
            }
            
            SkeletonView(height: 14)
            SkeletonView(width: 200, height: 14)
        }
        .padding(20)
        .background(DeevoColors.surface)
        .cornerRadius(16)
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(DeevoColors.border, lineWidth: 1)
        )
    }
}

// MARK: - Skeleton List (for Inbox)

public struct SkeletonClaimsList: View {
    let count: Int
    
    public init(count: Int = 5) {
        self.count = count
    }
    
    public var body: some View {
        VStack(spacing: 16) {
            ForEach(0..<count, id: \.self) { _ in
                SkeletonCard()
            }
        }
        .padding(.horizontal)
    }
}

// MARK: - Skeleton Claim Detail

public struct SkeletonClaimDetail: View {
    public init() {}
    
    public var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                // Header
                VStack(alignment: .leading, spacing: 12) {
                    SkeletonView(width: 200, height: 28)
                    SkeletonView(width: 120, height: 16)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                
                // Status Card
                HStack(spacing: 16) {
                    ForEach(0..<3, id: \.self) { _ in
                        VStack(spacing: 8) {
                            SkeletonView(width: 60, height: 32)
                            SkeletonView(width: 80, height: 14)
                        }
                        .frame(maxWidth: .infinity)
                        .padding(16)
                        .background(DeevoColors.surface)
                        .cornerRadius(12)
                    }
                }
                
                // Details Section
                VStack(alignment: .leading, spacing: 16) {
                    SkeletonView(width: 120, height: 20)
                    
                    ForEach(0..<4, id: \.self) { _ in
                        HStack {
                            SkeletonView(width: 100, height: 16)
                            Spacer()
                            SkeletonView(width: 150, height: 16)
                        }
                    }
                }
                .padding(20)
                .background(DeevoColors.surface)
                .cornerRadius(16)
                
                // AI Section
                VStack(alignment: .leading, spacing: 16) {
                    SkeletonView(width: 150, height: 20)
                    SkeletonView(height: 80, cornerRadius: 12)
                    HStack(spacing: 12) {
                        SkeletonView(width: 100, height: 36, cornerRadius: 8)
                        SkeletonView(width: 100, height: 36, cornerRadius: 8)
                    }
                }
                .padding(20)
                .background(DeevoColors.surface)
                .cornerRadius(16)
            }
            .padding()
        }
    }
}

// MARK: - Skeleton Sync Queue

public struct SkeletonSyncQueue: View {
    public init() {}
    
    public var body: some View {
        VStack(spacing: 16) {
            // Summary Card
            HStack(spacing: 20) {
                ForEach(0..<3, id: \.self) { _ in
                    VStack(spacing: 8) {
                        SkeletonView(width: 40, height: 28)
                        SkeletonView(width: 60, height: 12)
                    }
                }
            }
            .padding(20)
            .frame(maxWidth: .infinity)
            .background(DeevoColors.surface)
            .cornerRadius(16)
            
            // Queue Items
            ForEach(0..<4, id: \.self) { _ in
                HStack {
                    SkeletonView(width: 40, height: 40, cornerRadius: 8)
                    VStack(alignment: .leading, spacing: 6) {
                        SkeletonView(width: 180, height: 14)
                        SkeletonView(width: 100, height: 12)
                    }
                    Spacer()
                    SkeletonView(width: 60, height: 24, cornerRadius: 12)
                }
                .padding(16)
                .background(DeevoColors.surface)
                .cornerRadius(12)
            }
        }
        .padding(.horizontal)
    }
}

// MARK: - Preview

#Preview {
    ScrollView {
        VStack(spacing: 32) {
            Text("Skeleton Components")
                .font(DeevoTypography.headlineLarge)
                .foregroundColor(DeevoColors.textPrimary)
            
            SkeletonView(width: 200, height: 20)
            
            SkeletonCard()
            
            Text("Claims List Loading")
                .font(DeevoTypography.labelMedium)
                .foregroundColor(DeevoColors.textSecondary)
            
            SkeletonClaimsList(count: 2)
        }
        .padding()
    }
    .background(DeevoColors.backgroundDark)
}
