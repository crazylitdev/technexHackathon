import os
from os import environ
from pathlib import Path
from dataclasses import dataclass

environ = environ.get


@dataclass
class Settings:

    baseDir = Path(os.path.split(os.path.abspath(__file__))[0])
    assets: Path = baseDir / "gui" / "assets"

    refreshTime: int = environ("cameraRefreshTime", 2)

    debugData = environ("debugData", False)
    debugDataLocation = environ("debugDataLocation", baseDir / "capturers" / "data")

    guiFilePath: Path = environ("guiFilePath", assets / "guiMain.ui")
    styleFilePath: Path = environ("styleFilePath", assets / "style.css")
    
    staticFilePath = environ("staticFilePath", baseDir / "capturers" / "data" / "man.png")
    staticVideoPath = environ("staticVideoPath")


settings = Settings()
