import sys
import open3d as o3d

def check_file_ending(path):
    file_ending = path.split(".")[-1]
    print("     ending", file_ending)
    if file_ending == "pcd" or file_ending == "ply":
        return True
    return False


def open_file(file_path):
    try:
        o3d.visualization.draw_geometries([o3d.io.read_point_cloud(file_path)])
    except Exception as e:
        print("Could not open file:", file_path)
        print(e)

if __name__ == "__main__":
    inputs = sys.argv[1:]
    for input in inputs:
        print(f"## Opening {input} ##")
        if check_file_ending(input):
            open_file(input)
        else:
            print("     --> wrong filetype")