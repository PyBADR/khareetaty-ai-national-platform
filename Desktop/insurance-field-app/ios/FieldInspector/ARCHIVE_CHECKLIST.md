# Archive Checklist - FieldInspector

## Pre-Archive Verification

### 1. Build Configuration

- [ ] **Scheme**: `FieldInspector`
- [ ] **Configuration**: `Release`
- [ ] **Destination**: `Any iOS Device (arm64)`
- [ ] **Swift Optimization**: `-O` (Optimize for Speed)
- [ ] **Strip Debug Symbols**: Yes

### 2. Signing & Capabilities

- [ ] **Team**: Select valid Apple Developer Team
- [ ] **Bundle Identifier**: `com.fieldinsurance.FieldInspector`
- [ ] **Signing Certificate**: `Apple Distribution` (for App Store) or `Apple Development` (for TestFlight)
- [ ] **Provisioning Profile**: `Xcode Managed Profile` or manual profile

### 3. Capabilities Verification

| Capability | Required | Configured |
|------------|----------|------------|
| Camera | Yes | ✅ |
| Microphone | Yes | ✅ |
| Photo Library | Yes | ✅ |
| Location (When In Use) | Optional | Check |
| Background Modes | Optional | Check |

### 4. Privacy Manifest (PrivacyInfo.xcprivacy)

- [ ] File exists in project
- [ ] Required reason APIs declared:
  - [ ] `NSPrivacyAccessedAPICategoryFileTimestamp` (if using file timestamps)
  - [ ] `NSPrivacyAccessedAPICategoryUserDefaults` (for UserDefaults)
  - [ ] `NSPrivacyAccessedAPICategoryDiskSpace` (if checking disk space)

### 5. Info.plist Permission Strings

| Key | Value | Status |
|-----|-------|--------|
| `NSCameraUsageDescription` | "This app needs camera access to capture inspection photos" | ✅ |
| `NSMicrophoneUsageDescription` | "Required to record voice notes for inspection audit trail" | ✅ |
| `NSPhotoLibraryUsageDescription` | "Access photos for inspection documentation" | Check |
| `NSLocationWhenInUseUsageDescription` | "Location is used to tag inspection photos" | Check |

### 6. App Icons & Launch Screen

- [ ] App icon set complete (all sizes)
- [ ] Launch screen configured
- [ ] iPad-specific icons if needed

---

## Archive Process

### Step 1: Clean Build
```bash
xcodebuild clean -project FieldInspector.xcodeproj -scheme FieldInspector
```

### Step 2: Archive
```bash
xcodebuild archive \
  -project FieldInspector.xcodeproj \
  -scheme FieldInspector \
  -destination 'generic/platform=iOS' \
  -archivePath ./build/FieldInspector.xcarchive
```

Or via Xcode:
1. Product → Archive
2. Wait for build to complete
3. Organizer window opens automatically

### Step 3: Validate Archive

In Xcode Organizer:
1. Select the archive
2. Click "Validate App"
3. Select distribution method (App Store Connect)
4. Review and fix any issues

Common validation issues:
- Missing privacy manifest
- Invalid provisioning profile
- Missing required icons
- Unsupported architectures

### Step 4: Export/Distribute

**For TestFlight:**
1. Click "Distribute App"
2. Select "App Store Connect"
3. Select "Upload"
4. Follow prompts

**For Ad Hoc/Enterprise:**
1. Click "Distribute App"
2. Select "Ad Hoc" or "Enterprise"
3. Select provisioning profile
4. Export IPA

---

## Post-Archive Verification

### TestFlight
- [ ] Build appears in App Store Connect
- [ ] No missing compliance issues
- [ ] Export compliance answered
- [ ] Internal testing group notified

### App Store
- [ ] Screenshots uploaded (iPad required)
- [ ] App description complete
- [ ] Privacy policy URL valid
- [ ] Support URL valid
- [ ] Age rating questionnaire complete

---

## Troubleshooting

### "Signing for FieldInspector requires a development team"
1. Open project in Xcode
2. Select FieldInspector target
3. Signing & Capabilities tab
4. Select Team from dropdown
5. Enable "Automatically manage signing"

### "No profiles for 'com.fieldinsurance.FieldInspector'"
1. Ensure bundle ID matches App Store Connect app
2. Regenerate provisioning profiles in Apple Developer Portal
3. Download profiles: Xcode → Preferences → Accounts → Download Manual Profiles

### "Missing Privacy Manifest"
1. Create `PrivacyInfo.xcprivacy` file
2. Add to target's Copy Bundle Resources
3. Declare required reason APIs

### Archive validation fails with API usage
1. Check third-party SDK privacy manifests
2. Update SDKs to versions with privacy manifests
3. Add missing declarations to app's privacy manifest

---

## CI/CD Integration

See `.github/workflows/build.yml` for automated build configuration.

Key environment variables:
- `APPLE_TEAM_ID`: Apple Developer Team ID
- `MATCH_PASSWORD`: Fastlane match password (if using)
- `APP_STORE_CONNECT_API_KEY`: For automated uploads

---

## Version Checklist

Before each release:
- [ ] Increment version number in project settings
- [ ] Increment build number
- [ ] Update CHANGELOG.md
- [ ] Tag release in git: `git tag -a v1.0.0 -m "Release 1.0.0"`
- [ ] Push tags: `git push origin --tags`
