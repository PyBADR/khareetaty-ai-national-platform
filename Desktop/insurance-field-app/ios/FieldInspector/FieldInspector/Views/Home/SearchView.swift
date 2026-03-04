import SwiftUI

struct SearchView: View {
    @State private var searchText = ""
    @State private var searchResults: [Claim] = []
    @State private var isSearching = false
    @State private var hasSearched = false
    
    var body: some View {
        VStack(spacing: 0) {
            // Search bar
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)
                
                TextField("Search claims by number, customer, or plate...", text: $searchText)
                    .textFieldStyle(.plain)
                    .onSubmit {
                        performSearch()
                    }
                
                if !searchText.isEmpty {
                    Button(action: {
                        searchText = ""
                        searchResults = []
                        hasSearched = false
                    }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.secondary)
                    }
                }
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(10)
            .padding()
            
            Divider()
            
            // Results
            if isSearching {
                Spacer()
                ProgressView("Searching...")
                Spacer()
            } else if hasSearched && searchResults.isEmpty {
                Spacer()
                VStack(spacing: 16) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 60))
                        .foregroundColor(.secondary)
                    Text("No results found")
                        .font(.headline)
                    Text("Try a different search term.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                Spacer()
            } else if !hasSearched {
                Spacer()
                VStack(spacing: 16) {
                    Image(systemName: "magnifyingglass")
                        .font(.system(size: 60))
                        .foregroundColor(.secondary)
                    Text("Search Claims")
                        .font(.headline)
                    Text("Enter a claim number, customer name, or license plate to search.")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding()
                Spacer()
            } else {
                List(searchResults) { claim in
                    NavigationLink(value: claim) {
                        ClaimRowView(claim: claim)
                    }
                }
                .listStyle(.plain)
            }
        }
        .navigationTitle("Search")
        .navigationDestination(for: Claim.self) { claim in
            ClaimDetailView(claim: claim)
        }
    }
    
    private func performSearch() {
        guard !searchText.isEmpty else { return }
        
        isSearching = true
        hasSearched = true
        
        Task {
            do {
                let response = try await APIService.shared.getClaims(search: searchText)
                await MainActor.run {
                    searchResults = response.claims
                    isSearching = false
                }
            } catch {
                await MainActor.run {
                    searchResults = []
                    isSearching = false
                }
            }
        }
    }
}

#Preview {
    NavigationStack {
        SearchView()
    }
}
