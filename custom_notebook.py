import json
import argparse
import os
from shutil import copyfile

def hideCells(notebook):
    """
    Finds the tag 'hide' in each cell and removes it

    Returns dict without 'hide' tagged cells
    """
    clean = []
    for cell in notebook['cells']:
        try:
            if 'hide' in cell['metadata']['tags']:
                pass
            else:
                clean.append(cell)
        except KeyError:
            clean.append(cell)

    notebook['cells'] = clean

    return notebook

def keepCells(notebook):
    """
    Finds the tag 'keep' in any cell and if it exists,
    remove the ones that don't have it

    Returns dict without 'hide' tagged cells
    """
    has_keep = False
    for cell in notebook['cells']:
        try:
            if 'keep' in cell['metadata']['tags']:
                has_keep = True
                break
        except KeyError:
            pass

    if has_keep:
        clean = []
        for cell in notebook['cells']:
            try:
                if 'keep' in cell['metadata']['tags']:
                    
                    clean.append(cell)
            except KeyError:
                pass

        
        notebook['cells'] = clean

    return notebook

def emptyCells(notebook):
    """
    Finds the tag 'empty' in each cell and removes its content

    Returns dict with empty cells
    """

    clean = []
    for cell in notebook['cells']:
        try:
            tags = cell['metadata']['tags']
            if True in map(lambda x: x.lower().startswith('empty'), tags):
                cell['source'] = []
                clean.append(cell)

        except KeyError:
            clean.append(cell)

    notebook['cells'] = clean

    return notebook

def exCells(notebook):
    """
    Finds the tag 'exe' in each cell and applies HTML template

    Returns dict with template cells
    """
    clean = []
    wraphead = ["<div class=\"alert alert-success\">\n",
                "<b>Exercise</b>:\n",
                "<ul>\n",
                "<li>\n"]

    wraptail = ["</li>\n",
                "<p>\n",
                "</ul>\n",
                "</div>"]

    for cell in notebook['cells']:
        
        try:
            tags = cell['metadata']['tags']
            if True in map(lambda x: x.lower().startswith('ex'), tags):
                cell['source'] = wraphead + cell['source'] + wraptail
                clean.append(cell)
            else:
                clean.append(cell)
        except KeyError:
            clean.append(cell)
    notebook['cells'] = clean

    return notebook

def hideCode(notebook):
    """
    Finds the tags '#!--' and '#--! in each cell and removes
    the lines in between.

    Returns dict
    """

    for i, cell in enumerate(notebook['cells']):
        istart = 0
        istop = -1
        for idx, line in enumerate(cell['source']):
            if '#!--' in line:
                istart = idx
            if '#--!' in line:
                istop = idx

        notebook['cells'][i]['source'] = cell['source'][:istart] + cell['source'][istop+1:]

    return notebook

def hideToolbar(notebook):
    """
    Finds the display toolbar tag and hides it
    """

    if 'celltoolbar' in notebook['metadata']:
        del notebook['metadata']['celltoolbar']

    return notebook

def stripout(fname):
    """
    Removes all output cells
    """

    response = os.system("nbstripout {}".format(fname))

    return

def process(fname,
            outname,
            poutput=True,
            pkeep=True,
            phide=True,
            pexercise=True,
            phidecode=True):
    """
    Loads an 'ipynb' file as a dict and performs cleaning tasks

    Writes cleaned version
    """
    if poutput:
        stripout(fname)

    with open(fname, 'r') as f:
        notebook_s = f.read()

    notebook = json.loads(notebook_s)

    if pkeep:
        notebook = keepCells(notebook)
    if phide:
        notebook = hideCells(notebook)
    if pexercise:
        notebook = exCells(notebook)
    if phidecode:
        notebook = hideCode(notebook)

    hideToolbar(notebook)

    with open(outname, 'w') as f:
        _ = f.write(json.dumps(notebook))

    return

def makedirs(name):
    """
    """

    try:
        os.mkdir(name)
    except:
        pass

    return

def movefiles(names, dest):
    """
    """
    for name in names:
        copyfile(name.strip('\n'), dest+'/'+name.strip('\n'))

    return

def processList(fname):
    """
    Loads an 'txt' file with notebook filenames
    and performs cleaning tasks on them

    Writes cleaned version
    """
    with open(fname, 'r') as f:
        notebook_list = f.readlines()

    student = 'student'
    instructor = 'instructor'
    makedirs(student)
    makedirs(instructor)

    movefiles(notebook_list, student)
    movefiles(notebook_list, instructor)

    cwd = os.getcwd()

    os.chdir(os.path.join(cwd, student))
    for name in notebook_list:
        fname = name.strip('\n')
        process(fname, fname)

    # os.chdir(os.path.join(cwd, instructor))
    # for name in notebook_list:
    #     fname = name.strip('\n')
    #     process(fname, fname,
    #             poutput=True,
    #             pkeep=False,
    #             phide=False,
    #             pexercise=True,
    #             phidecode=False)
    

    return


def main(argv=None):
    """
    Usage:

    python custom_notebook.py --infile name.ipynb --outfile out.ipynb
    """
    argp = argparse.ArgumentParser(description='Convert a set of notebooks')
    argp.add_argument('--infile', nargs='?', type=str, default='.',
                      help='The .ipynb file')
    argp.add_argument('--outfile', type=str, default='processed.ipynb',
                      help='Output filename.')
    argp.add_argument('--listfile', type=str, default='notebooks.txt',
                      help='Text file with Notebook filenames')
    args = argp.parse_args(argv)

    # process(args.infile, args.outfile)
    processList(args.listfile)


if __name__ == '__main__':
    main()
