# Email signature

Source for the HTML email signature, plus the images it references. GitHub Pages serves
the images over https so they load in any mail client.

Preview: https://xsovad06.github.io/email-signature/

## Files

| Path | Purpose |
|---|---|
| `damian-sova-signature.html` | The signature. Single source of truth. |
| `assets/` | Images, referenced from the HTML by absolute Pages URL |
| `install-apple-mail.py` | Writes the signature into Apple Mail |
| `index.html` | Preview page served at the Pages URL |

## Updating

1. Edit `damian-sova-signature.html`.
2. Commit and push. Pages redeploys in well under a minute.
3. Reinstall into the mail client (see below).

Images are referenced by absolute URL, so replacing a file in `assets/` takes effect
everywhere as soon as it is pushed, with no reinstall. Changing the HTML does need a
reinstall, because each mail client keeps its own copy.

## Installing

### Gmail

Open https://xsovad06.github.io/email-signature/damian-sova-signature.html, select all,
copy, then paste into Gmail Settings, General, Signature. Gmail re-hosts pasted images
on its own CDN.

### Apple Mail

Pasting does not work here. Mail's paste converter flattens the nested tables and renders
every image at its natural pixel size. Write the signature files directly instead:

1. Create the signature in Mail if it does not exist yet (Settings, Signatures, click +),
   so the installer has a file to write into.
2. Quit Mail completely.
3. Run `python3 install-apple-mail.py`
4. Start Mail and check a new compose window, which renders more faithfully than the
   preview pane in Settings.
5. Uncheck "Always match my default message font", or Mail overrides the styling.

The script targets the signatures named `Redhat` and `Damian` by default. Pass names to
target others: `python3 install-apple-mail.py Sovicka`

It needs Full Disk Access (System Settings, Privacy and Security, Full Disk Access) for
whichever terminal or editor runs it, and that app must be fully quit and reopened after
granting it, since the permission is only read at process launch.

### Two traps worth knowing

1. **Signatures sync through iCloud.** The source of truth is
   `~/Library/Mobile Documents/com~apple~mail/Data/V4/Signatures/`, not
   `~/Library/Mail/V10/MailData/Signatures/`. The second is a mirror that Mail restores
   from iCloud on launch, silently discarding anything written only there. The installer
   writes every store it finds.
2. **`.mailsignature` files must use LF line endings.** CRLF makes Mail parse the
   signature as empty and reset `SignatureIsRich` to false. The symptom is a blank
   signature plus an "Always match my default message font" checkbox that will not stay
   unchecked.

Editing a signature inside Mail's UI overwrites the custom HTML, so re-run the installer
after any such edit.

## Regenerating assets

Logos and icons are committed at twice their display size and scaled down by the
`width` and `height` attributes in the HTML, so they stay sharp on retina screens.

On macOS, convert SVG to PNG with `sips`, which honours the viewBox:

```bash
sips -s format png logo.svg --out logo.png
```

Avoid `qlmanage -t` for this. It pads the output to a square and clips wide artwork.
To rasterize at higher resolution, raise the `width` and `height` attributes on the
`<svg>` element, leaving `viewBox` untouched, before converting.

Logo artwork drawn for a dark background (white wordmark) needs recolouring first, or it
is invisible on the signature's white card.
