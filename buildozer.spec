
[app]
title = BDG OCR PRO
package.name = bdg_ocr_pro
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.2
requirements = python3,kivy,requests,plyer
presplash.filename = %(source.dir)s/logo.png
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.debug = 1

[buildozer]
log_level = 2
