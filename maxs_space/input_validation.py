import sys

USAGE_MESSAGE = "Usage: python patterfier_v1.py <pattern_overlay_path> <image_path>"
CALLER = "input_validation.validate(): "

def validate(version):
    if version != 1:
        print(CALLER + "That version is not supported yet")
        exit()
    # 2 arguments are given
    if (len(sys.argv) != 3):
        print(CALLER + USAGE_MESSAGE)
        exit()
    # Path arguments exist in the FS
    if (not os.path.exists(sys.argv[0])) or (not os.path.exists(sys.argv[1])):
        print(CALLER + "Please make sure that image paths are valid")
        print(CALLER + USAGE_MESSAGE)
        exit()
