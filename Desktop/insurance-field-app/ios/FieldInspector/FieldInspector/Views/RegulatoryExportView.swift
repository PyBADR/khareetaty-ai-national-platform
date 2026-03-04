import SwiftUI

struct RegulatoryExportView: View {
    var body: some View {
        VStack {
            Image(systemName: "square.and.arrow.up")
                .font(.largeTitle)
                .foregroundColor(DeevoColors.accent)
            Text("Regulatory Export")
                .font(.title)
            Text("Coming Soon")
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(DeevoColors.backgroundDark)
    }
}

#Preview {
    RegulatoryExportView()
}
