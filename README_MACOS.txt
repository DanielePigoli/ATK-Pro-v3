================================================================================
  ATK-Pro v3.0 for macOS - Installation Instructions
================================================================================

SYSTEM REQUIREMENTS:
  - macOS 12.0 (Monterey) or later
  - Processor: Intel (x86_64) native  |  Apple Silicon (M1/M2/M3…) via Rosetta 2
    Rosetta 2 is pre-installed on all Apple Silicon Macs with macOS 11+.
    If not present, macOS will prompt you to install it automatically.
  - Internet connection to download Playwright browsers on first launch
  - Python 3.12 is already bundled inside ATK-Pro.app

ABOUT THIS BUILD:
  This build is compiled for Intel (x86_64) and runs on all modern Macs:
    • Intel Macs   → runs natively
    • Apple Silicon (M1/M2/M3…) → runs via Rosetta 2, which is transparent
      and seamless — no performance difference for typical workloads.

  The build is not signed with an Apple Developer certificate (requires a
  paid Apple Developer membership). It IS ad-hoc signed, which means macOS
  recognizes it as an intentional app and the methods below work reliably.

HOW TO OPEN ATK-Pro (choose one method):

────────────────────────────────────────────────────────────────────────────
  METHOD 1 — Remove quarantine attribute (RECOMMENDED, works on all versions)
────────────────────────────────────────────────────────────────────────────
  1. Drag ATK-Pro.app to your Applications folder.
  2. Open Terminal (Applications > Utilities > Terminal).
  3. Run:
       xattr -cr /Applications/ATK-Pro.app
  4. Open ATK-Pro normally from your Applications folder.

────────────────────────────────────────────────────────────────────────────
  METHOD 2 — System Settings > Privacy & Security (macOS 13+)
────────────────────────────────────────────────────────────────────────────
  1. Try to open ATK-Pro.app — macOS will block it and show a dialog.
  2. Go to System Settings > Privacy & Security.
  3. Scroll to the "Security" section.
  4. Click "Open Anyway" next to the ATK-Pro message.
  5. Confirm with your password.
  NOTE: If "Open Anyway" does not appear, use Method 1.

────────────────────────────────────────────────────────────────────────────
  METHOD 3 — Control+Click (older macOS versions)
────────────────────────────────────────────────────────────────────────────
  1. Locate ATK-Pro.app in Finder.
  2. Hold Control and click the icon.
  3. Select "Open" from the context menu.
  4. Click "Open" again in the confirmation dialog.

FIRST LAUNCH:
  ATK-Pro will automatically download Chromium (~150 MB) on first use.
  This may take a few minutes. An internet connection is required.

DISCLAIMER:
  ATK-Pro is intended for archival, genealogical, and document consultation
  workflows, primarily in support of the Portale Antenati.
  Access to third-party resources is accessory and depends on their technical
  and legal availability. The user is solely responsible for complying with
  each portal's terms of use, licenses, copyright rules, access conditions,
  and reuse policies.
  ATK-Pro is not intended for automated data extraction, mass harvesting,
  systematic downloads, or bypassing authenticated access, subscriptions,
  paywalls, technical restrictions, security measures, or contractual
  prohibitions imposed by third-party sites or portals.
  Commercial genealogy portals or portals requiring an account are not
  supported unless explicit documented authorization says otherwise.
  The software is provided "AS IS", without warranty of any kind.
  The authors assume no liability for improper or unlawful use.

SUPPORT:
  GitHub : https://github.com/DanielePigoli/ATK-Pro-v3
  Issues : https://github.com/DanielePigoli/ATK-Pro-v3/issues

================================================================================
  (c) 2026 ATK-Pro - See the bundled legal disclaimer for terms of use
================================================================================
