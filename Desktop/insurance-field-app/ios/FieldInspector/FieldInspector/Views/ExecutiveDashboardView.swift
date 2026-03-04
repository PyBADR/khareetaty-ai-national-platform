import SwiftUI

struct ExecutiveDashboardView: View {
    var body: some View {
        VStack {
            Image(systemName: "chart.bar.fill")
                .font(.largeTitle)
                .foregroundColor(DeevoColors.accent)
            Text("Executive Dashboard")
                .font(.title)
            Text("Coming Soon")
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(DeevoColors.backgroundDark)
    }
}

#Preview {
    ExecutiveDashboardView()
}
