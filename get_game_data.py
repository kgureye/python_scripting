import os
import json
import shutil
from subprocess import PIPE, run
import sys


GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]


def find_all_game_paths(source):
    # Traverse, match if pattern is found and get us the path
    game_paths = []

    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)

        break

    return game_paths


def get_name_from_paths(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path) # gives us last part of the path
        new_dir_name = dir_name.replace(to_strip, "") #replace whatever we want with nothing.
        new_names.append(new_dir_name)

    return new_names


def create_dir(path):
    #if dir does not exist, create it
    if not os.path.exists(path):
        os.mkdir(path)


# take a source and a destination, and copy the source into the destination.
def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source, dest)


#JSON file that has metadata about the different games and how many of them there are.
def make_json_metadata_file(path, game_dirs):
    data = {
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }

    with open(path, "w") as f:
        json.dump(data, f)


def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
                break

        break

    if code_file_name is None:
        return

    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)


def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path) #chdir - change directory

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True) 
    print("compile result", result)

    os.chdir(cwd) #change back to the original directory in case we want to run it again

# function for taking all the directories and copying them to the target directory while removing the game part.
def main(source, target):
    cwd = os.getcwd()  # cwd = current working directory, meaning the directory you're currently in.
    source_path = os.path.join(cwd, source) #will join the path regardless of what OS you're working on. This is preferable to creating string concatenations.
    target_path = os.path.join(cwd, target)

    game_paths = find_all_game_paths(source_path)
     #get the destination paths
    new_game_dirs = get_name_from_paths(game_paths, "_game")

    create_dir(target_path)

    # zip will take matching elements from two arrays, combine them into a tuple and give me access.
    for src, dest in zip(game_paths, new_game_dirs):
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path) #compile the game code in the destination path.

    json_path = os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        raise Exception("You must pass a source and target directory - only.")

    source, target = args[1:]
    main(source, target)