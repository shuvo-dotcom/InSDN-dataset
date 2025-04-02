[app]
title = InSDN Anomaly Detection
package.name = insdn
package.domain = org.insdn
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy,numpy,pandas,matplotlib,scikit-learn,tqdm,plotly,networkx,python-dotenv,psutil,netifaces,requests,torch,openai

orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.1
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.ndk = 25.2.9519653
android.sdk = 31
android.accept_sdk_license = True
android.arch = arm64-v8a

# (list) Android application meta-data to set (key=value format)
android.meta_data =

# (list) Android library project to add (will be added in the
# project.properties automatically.)
android.library_references =

# (list) Android shared libraries which will be added to AndroidManifest.xml using <uses-library> tag
android.uses_library =

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
# use that parameter together with android.entrypoint to set custom Java class instead of PythonActivity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <manifest> element of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML code
#android.extra_manifest_xml = ./src/android/extra_manifest.xml

# (str) Extra xml to write directly inside the <manifest><application> tag of AndroidManifest.xml
# use that parameter to provide a filename from where to load your custom XML arguments:
#android.extra_manifest_application_arguments = ./src/android/extra_manifest_application_arguments.xml

[buildozer]
log_level = 2
warn_on_root = 1 