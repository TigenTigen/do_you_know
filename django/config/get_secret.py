def get_secret(path):
    secret_file = open(path, 'r')
    for line in secret_file:
        return line[0:-1]
