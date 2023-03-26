import argparse
import os
import time
import tkinter as tk
from tkinter import filedialog
from AbbyyOnlineSdk import *

processor = None


def setup_processor():
    if "ABBYY_APPID" in os.environ:
        processor.ApplicationId = os.environ["ABBYY_APPID"]

    if "ABBYY_PWD" in os.environ:
        processor.Password = os.environ["ABBYY_PWD"]

    # Proxy settings
    if "http_proxy" in os.environ:
        proxy_string = os.environ["http_proxy"]
        print("Using http proxy at {}".format(proxy_string))
        processor.Proxies["http"] = proxy_string

    if "https_proxy" in os.environ:
        proxy_string = os.environ["https_proxy"]
        print("Using https proxy at {}".format(proxy_string))
        processor.Proxies["https"] = proxy_string


# Recognize a file at filePath and save result to resultFilePath
def recognize_file(file_path, result_file_path, language, output_format):
    print("Uploading..")
    settings = ProcessingSettings()
    settings.Language = language
    settings.OutputFormat = output_format
    task = processor.process_image(file_path, settings)
    if task is None:
        print("Error")
        return
    if task.Status == "NotEnoughCredits":
        print("Not enough credits to process the document. Please add more pages to your application's account.")
        return

    print("Id = {}".format(task.Id))
    print("Status = {}".format(task.Status))

    # Wait for the task to be completed
    print("Waiting..")


    while task.is_active():
        time.sleep(5)
        print(".")
        task = processor.get_task_status(task)

    print("Status = {}".format(task.Status))

    if task.Status == "Completed":
        if task.DownloadUrl is not None:
            processor.download_result(task, result_file_path)
            print("Result was written to {}".format(result_file_path))
    else:
        print("Error processing task")


def create_parser():
    parser = argparse.ArgumentParser(description="Recognize a file via web service")
    parser.add_argument('source_file')
    parser.add_argument('target_file')

    parser.add_argument('-l', '--language', default='English', help='Recognition language (default: %(default)s)')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-txt', action='store_const', const='txt', dest='format', default='txt')
    group.add_argument('-pdf', action='store_const', const='pdfSearchable', dest='format')
    group.add_argument('-rtf', action='store_const', const='rtf', dest='format')
    group.add_argument('-docx', action='store_const', const='docx', dest='format')
    group.add_argument('-xml', action='store_const', const='xml', dest='format')

    return parser


def openFileToUpload():
    global source_file
    filepath = filedialog.askopenfilename()
    print(type(filepath))
    source_file = filepath
    print(source_file)
    global target_file
    target_file = source_file[0:len(source_file) - 4] + "_output.txt"


def downloadFile():
    file = filedialog.asksaveasfile(defaultextension='.txt', filetypes=[
        ("Text file,"".txt"),
    ])


def target_file_set(source_file):
    return source_file + "output.txt"


def main():
    print("aaa")
    global processor
    processor = AbbyyOnlineSdk()

    setup_processor()
    args = create_parser().parse_args()

    language = args.language
    output_format = args.format

    # source_file = None

    screen = tk.Tk()
    width = 200
    height = 200
    screen_width = screen.winfo_screenwidth()  # Width of the screen
    screen_height = screen.winfo_screenheight()  # Height of the screen

    # Calculate Starting X and Y coordinates for Window
    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    x = int(x)
    y = int(y)

    screen.title("pdf-img converter")

    lbl_upload = tk.Label(text=("pdf img converter"), font='Times 15')
    btn_upload = tk.Button(text="Choose File", command=openFileToUpload)

    lbl_spacer = tk.Label()
    lbl_spacer1 = tk.Label()

    btn_execute = tk.Button(text="Execute", command=lambda: execute(source_file, target_file, language, output_format))
    lbl_spacer1.pack()
    lbl_upload.pack()
    btn_upload.pack()
    lbl_spacer.pack()

    lbl_spacer.pack()
    btn_execute.pack()
    screen.geometry("300x150+{}+{}".format(x, y))
    screen.resizable(False, False)
    screen.mainloop()


def execute(source_file, target_file, language, output_format):
    print(source_file)
    if os.path.isfile(source_file):
        recognize_file(source_file, target_file, language, output_format)
    else:
        print("No such file: {}".format(source_file))


if __name__ == "__main__":
    main()
