def read_names_from_file(filename):
    with open(filename, 'r') as file:
        names = file.readlines()
        return [name.strip() for name in names]


def write_names_to_file(filename, names):
    with open(filename, 'w') as file:
        for name in names:
            file.write(name + '\n')


def main():
    # Read names from two files
    file1_names = read_names_from_file('/home/tes_unreal/PycharmProjects/anovox/Tools/all.txt')
    file2_names = read_names_from_file('/home/tes_unreal/PycharmProjects/anovox/Tools/anomaly_names.txt')

    # Check which names are in file1 but not in file2
    names_not_in_file2 = [name for name in file1_names if name not in file2_names]

    # Write the names not in file2 to a new file
    write_names_to_file('names_not_in_file2.txt', names_not_in_file2)


if __name__ == "__main__":
    main()
