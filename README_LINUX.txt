================================================================================
  ATK-Pro v3.0 for Linux - Instructions
================================================================================

SYSTEM REQUIREMENTS:
  - Linux x86_64 (Ubuntu 20.04+, Debian 11+, Fedora 34+, etc.)
  - Internet connection to download the Playwright browser on first launch

INSTALLATION — choose one method:

  METHOD A — DEB package (Ubuntu/Debian, recommended):
    Double-click ATK-Pro-Linux.deb in your file manager, OR:
      sudo dpkg -i ATK-Pro-Linux.deb
      sudo apt-get install -f       # fixes missing deps if any
    The application will appear in your Applications menu.

  METHOD B — Tarball (all distributions):
    1. Extract:  tar -xzf ATK-Pro-Linux.tar.gz
    2. Allow:    chmod +x ATK-Pro
    3. Run:      ./ATK-Pro

FIRST LAUNCH:
  ATK-Pro will automatically download Chromium (~150 MB) on first use.
  This may take a few minutes. An internet connection is required.

MISSING DEPENDENCIES (tarball only — deb installs these automatically):
  Ubuntu/Debian:
    sudo apt-get install libxcb-xinerama0 libxcb-cursor0 \
                         libegl1 libdbus-1-3 libxkbcommon-x11-0
  Fedora/RHEL:
    sudo dnf install xcb-util-cursor libxkbcommon-x11 mesa-libEGL dbus-libs
  Arch Linux:
    sudo pacman -S xcb-util-cursor libxkbcommon-x11 mesa dbus

DESKTOP INTEGRATION (tarball only — deb handles this automatically):
  Create ~/.local/share/applications/atk-pro.desktop with:

    [Desktop Entry]
    Type=Application
    Name=ATK-Pro
    Comment=IIIF Archive Toolkit Professional
    Exec=/full/path/ATK-Pro
    Icon=/full/path/assets/common/grafici/ATK-Pro.ico
    Terminal=false
    Categories=Utility;Education;

  Replace /full/path/ with the actual location of ATK-Pro.

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
