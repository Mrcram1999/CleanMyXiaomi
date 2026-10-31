# Sources and evidence

Checked 2026-10-31. These support command semantics, setup and product limitations, **not the safety of removing any particular Xiaomi package**.

- [Android Developers: ADB](https://developer.android.com/tools/adb) — device authorization, serial selection and package-manager interface.
- [Android Developers: Platform Tools](https://developer.android.com/tools/releases/platform-tools) — official OS-specific downloads and release notes.
- [AOSP PackageManagerShellCommand](https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/services/core/java/com/android/server/pm/PackageManagerShellCommand.java) — enabled-state commands, including disable-user, enable and default-state. OEM behavior still requires actual testing.
- [Xiaomi 14T personalized ads](https://www.mi.com/global/support/faq/details/KA-507647/) — disabling personalization does not remove the same quantity of ads.
- [Redmi Note 13 Pro advertising](https://www.mi.com/global/support/faq/details/KA-492666/) — per-app ad/notification settings.
- [Xiaomi privacy support](https://privacy.mi.com/support/faq?locale=en) — privacy and personalization controls; exact paths vary.
- [CleanYourTV](https://github.com/Gathin23/cleanyourtv) — inspiration for an agent-led entry point, independently implemented here.

No upstream package-removal profile is reused and no real-device test is claimed. Do not treat these references as approval for a target package.
