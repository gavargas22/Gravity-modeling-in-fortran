from gmm.gm import GMModel
import tkinter as tk
from tkinter import filedialog
from gooey import Gooey, GooeyParser


@Gooey(
    program_name="Gravity and Magnetics Modeling",
    program_description="Software made by Dr. Serpa",
)
def test_simulation():
    try:
        root = tk.Tk()
        root.withdraw()
        # Get a file path from a file dialog
        file_path = ""
        file_path = filedialog.askopenfilename()
    except Exception:
        print("Using a file in the filesystem")
        file_path = "models/test1/test1.json"

    if file_path == "":
        print("Nothing to read")
    else:
        gm_model = GMModel(project_file=file_path, new_project=False)
        print(gm_model)


if __name__ == "__main__":
    print("main is run directly")
    test_simulation()
