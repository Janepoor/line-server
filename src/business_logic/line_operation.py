
def process_text():
    index_dict = dict()
    with open("resource/text.txt") as txt_file:
        lines = txt_file.readlines()
        for i, line in enumerate(lines):
            index_dict[i+1] = line
    return index_dict


def get_line():
    index_dict = process_text()

    return {"status": True, "content": " return line"}


