import os
from cx_Freeze import Executable, setup
import PyQt6

_PYQT6 = os.path.dirname(PyQt6.__file__)
_QT_PLUGINS = os.path.join(_PYQT6, "Qt6", "plugins")

build_exe_options = {
    "packages": [
        "config",
        "core",
        "ui",
        "serial",
        "serial.tools",
        "serial.tools.list_ports",
        "win32api",
        "PyQt6",
    ],
    "excludes": [
        "tkinter",
        "test",
        "unittest",
        "distutils",
        "setuptools",
        "pydoc",
    ],
    "include_files": [
        "requirements.txt",
        (
            os.path.join(_QT_PLUGINS, "platforms", "qwindows.dll"),
            os.path.join("PyQt6", "Qt6", "plugins", "platforms", "qwindows.dll"),
        ),
        (
            os.path.join(_QT_PLUGINS, "platforms", "qminimal.dll"),
            os.path.join("PyQt6", "Qt6", "plugins", "platforms", "qminimal.dll"),
        ),
        (
            os.path.join(_QT_PLUGINS, "platforms", "qoffscreen.dll"),
            os.path.join("PyQt6", "Qt6", "plugins", "platforms", "qoffscreen.dll"),
        ),
    ],
    "optimize": 2,
}

bdist_msi_options = {
    "upgrade_code": "{B8F4A2D1-3E5C-4A7B-9F0D-1C2E3D4F5A6B}",
    "add_to_path": False,
    "initial_target_dir": r"[ProgramFilesFolder]\All Process\DesktopViewWeight",
}

executable = Executable(
    script="main.py",
    target_name="DesktopViewWeight",
    base="gui",
    icon="icon.ico",
    shortcut_name="DesktopViewWeight",
    shortcut_dir="ProgramMenuFolder",
)

setup(
    name="DesktopViewWeight",
    version="1.0.0",
    description="Visor de peso de báscula por puerto serie",
    author="ALL PROCESS S.A.C.",
    author_email="",
    url="https://github.com/allprocess-stack/WeightDesktopApp.git",
    options={
        "build_exe": build_exe_options,
        "bdist_msi": bdist_msi_options,
    },
    executables=[executable],
)
