# pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="Wc182YLDR3SyvB0BItzE")
project = rf.workspace("sserg").project("dice-lum74")
version = project.version(1)
dataset = version.download("folder")
                