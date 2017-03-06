def get_version(version):
    "Returns a PEP 386-compliant version number from VERSION."
    # Now build the two parts of the version number:
    # main = X.Y[.Z]
    # sub = .devN - for pre-alpha releases
    #     | {a|b|c}N - for alpha, beta and rc releases

    main = get_main_version(version)

    sub = ''
    if version[3] != 'final':
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'c'}
        sub = mapping[version[3]] + str(version[4])

    return main + sub


def get_main_version(version):
    "Returns main version (X.Y[.Z]) from VERSION."
    parts = 2 if version[2] == 0 else 3
    return '.'.join(str(x) for x in version[:parts])


def get_stable_branch_name(version):
    parts = (version[0], version[1], 'x')
    return '.'.join(str(x) for x in parts)
