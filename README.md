# ATVHome Apps

The app catalog read by the **Store** app on ATVHome (jailbroken Apple TV 3, ATVKit).
The Store downloads `catalog.json` from this repository's `main` branch.

## Submitting an app

1. Build your app as a `.tvapp` bundle with ATVKit (start from `Examples/Hello`).
   `Info.plist` needs `CFBundleIdentifier`, `CFBundleShortVersionString`, `NSPrincipalClass`
   (a class adopting `ATVApp`), and an `AppIcon.png` (16:9, 640×360) in the bundle.
2. Package it: `tools/pack-tvapp.sh build/MyApp.tvapp <download URL> <icon URL>`.
   This writes `MyApp-<version>.zip` (one `MyApp.tvapp` folder inside) and prints its catalog entry.
3. Upload the zip somewhere permanent (a GitHub release on your own repo is best).
4. Open a pull request here that adds your entry to `catalog.json` and your icon to `icons/<id>.png`.

### Entry fields

| field | required | meaning |
|---|---|---|
| `id` | yes | bundle identifier, must match the app's Info.plist |
| `name` | yes | shown in the Store |
| `version` | yes | dotted numbers; must match `CFBundleShortVersionString`. Raise it to ship an update |
| `package` | yes | HTTPS URL of the zip |
| `sha256` | yes | SHA-256 of the zip — the Store refuses a download that doesn't match |
| `size` | no | bytes, shown in the Store |
| `author`, `description`, `icon` | no | shown on the app page |
| `minATVKit` | no | lowest ATVKit version the app needs (e.g. `0.2`) |

### Rules

- Apps run inside ATVHome with the same rights as ATVHome (root-free, user `mobile`), so
  reviewers read the source before merging. Link your source in the pull request.
- No piracy, no apps that bypass DRM, nothing that phones home without saying so.
- Updating: change `version`, `package`, `sha256` and `size` in one pull request.

The `validate` workflow checks every pull request: valid JSON, required fields, unique ids,
the zip downloads, its SHA-256 matches, it contains exactly one `.tvapp` whose Info.plist
id and version match the entry.

## ATVHome updates

`update.json` is the Software Update feed for ATVHome itself (Settings › System › Software
Update), next to the release package it points to (`ATVHome-<version>.tgz`). Both are made by
`make release` in ATV Revival and signed with the release key: an Apple TV only installs a
package whose signature and checksum check out, so don't edit these files by hand.
