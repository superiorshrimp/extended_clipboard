def loadConfig():
    with open("./config.txt", "r") as f:
        lines = [row.split("=") for row in f]
    for i in range(len(lines)):
        lines[i] = [lines[i][0], int(lines[i][1])]
    for line in lines:
        if line[0] == "mode":
            mode = line[1]
        elif line[0] == "width":
            width = line[1]
        elif line[0] == "height":
            height = line[1]
    return mode, width, height

def updateConfig(mode, width, height):
    conf = ""
    with open("config.txt", "w") as f:
        conf += "mode={}\n".format(mode)
        conf += "width={}\n".format(width)
        conf += "height={}\n".format(height)
        f.write(conf)