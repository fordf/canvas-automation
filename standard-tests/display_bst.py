    def __str__(self):
        """Return string depiction of tree."""
        if getattr(self, ROOT_ATTR) is None:
            return 'Empty'
        head = display_rows_from(getattr(self, ROOT_ATTR), 5, lambda n: getattr(n, VAL_ATTR))
        return head

    def disp(self):
        display(self)


import math
import curses
import shutil
import inspect
import sys

module = sys.modules[__name__]

def findmatch(members, common):
    def find_match(member):
        for potential in common:
            if potential in member[0].lower():
                return True
        return False
    return next(filter(find_match, members))

common_names = { # lowercased
    'tree': ['binarysearchtree', 'binarytree', 'bst', 'tree'],
    'node': ['node'],
    'root': ['root'],
    'value': ['value', 'val', 'data'],
    'left': ['left', 'l_child'],
    'right': ['right', 'r_child'],
    'parent': ['parent']
}


try:
    classes = inspect.getmembers(module, predicate=inspect.isclass)
    CLASSNAME, ClassDef = findmatch(classes, common_names['tree'])
    bst_class_attrs = ClassDef().__dict__.items()
    ROOT_ATTR = findmatch(bst_class_attrs, common_names['root'])[0]

    NODECLASSNAME, NodeClassDef = findmatch(classes, common_names['node'])
    node_class_attrs = NodeClassDef(0).__dict__.items()
    VAL_ATTR = findmatch(node_class_attrs, common_names['value'])[0]
    LEFT_ATTR = findmatch(node_class_attrs, common_names['left'])[0]
    RIGHT_ATTR = findmatch(node_class_attrs, common_names['right'])[0]
    PARENT_ATTR = findmatch(node_class_attrs, common_names['parent'])[0]
except (StopIteration, Exception):
    ClassDef = getattr(module, CLASSNAME)


def display_rows_from(root, num_rows, node_func, max_len=4, args=()):
    """Return printable tree."""
    width = shutil.get_terminal_size((96, 20)).columns
    rows = [[root]]

    for i in range(num_rows - 1):
        rows.append(children_of(rows[i]))
        if not any(rows[-1]):
            break

    vals = []
    for row in rows:
        vals.append([node_func(node, *args) if node else '_' for node in row])

    return stringify_rows(vals, width, max_len)


def display(binary_tree, num_rows=5, node_func=None, args=(), attrs=None):
    """Interactive print loop."""
    if getr(binary_tree, ROOT_ATTR) is None:
        print('Empty')
        return
    try:
        stdscr = curses.initscr()
        stdscr.keypad(True)
        curses.nonl()

        if node_func is None:
            if attrs is None:
                attrs = [VAL_ATTR]
            elif isinstance(attrs, str):
                attrs = [attrs]
            node_func = attrs_func
            args = [attrs]
        # furthest_right = binary_tree.node_furthest(RIGHT_ATTR)
        root = binary_tree.root
        top, prev_inp = 0, ''

        while True:
            # max_len = len(str(node_func(furthest_right, *args)))
            max_len = 4
            hunk = display_rows_from(root,
                                     num_rows,
                                     node_func,
                                     max_len=max_len,
                                     args=args)
            stdscr.clear()
            stdscr.addstr(hunk)

            valid_moves = 'ad'
            if top != 0:
                valid_moves += 'w'
            quits = {'q', 'quit', 'exit'}

            stdscr.addstr('q(uit)/attr/' + valid_moves + ': ')
            while True:
                inp = stdscr.getstr().decode()
                if inp == '':
                    inp = prev_inp
                else:
                    prev_inp = inp
                if inp in set(valid_moves) | quits:
                    break
                else:
                    try:
                        for attr in inp.split(':'):
                            getr(root, attr)
                        break
                    except AttributeError:
                        pass
            if inp in quits:
                break
            if inp in valid_moves:
                top += {'a': 1, 'w': -1, 'd': 1}[inp]
                root = {'a': getr(root, LEFT_ATTR),
                        'w': getr(root, PARENT_ATTR),
                        'd': getr(root, RIGHT_ATTR)}[inp]
            else:
                inp_list = inp.split(':')
                node_func = attrs_func
                args = [inp_list]

    except (KeyboardInterrupt, Exception):
        pass
    stdscr.keypad(False)
    curses.endwin()


def stringify_rows(rows, width, max_len):
    """Create tree string."""
    funcs = [math.floor, math.ceil]
    width += width % 2
    num_per = 1
    res = []
    for row in rows:
        rowstr = ''
        each_gets = width / num_per
        split_len = (width - (max_len * num_per)) / (num_per * 2)
        for x in range(num_per):
            rowstr += str(row[x]).center(max_len).join(' ' * funcs[x % 2](split_len) for x in range(2))
            each_currently_getting = len(rowstr) / (x + 1)
            if each_gets < each_currently_getting:
                rowstr = rowstr[:-1]
            elif each_gets > each_currently_getting:
                rowstr += ' '
        res.append(rowstr)
        num_per *= 2
    res = '\n'.join(res)
    return res


def children_of(nodes):
    """Return children of a list of nodes."""
    res = []
    for node in nodes:
        if node:
            res += [getattr(node, LEFT_ATTR), getattr(node, RIGHT_ATTR)]
        else:
            res += [None, None]
    return res


def attrs_func(node, attrs):
    """Get all attrs of a node, separated by colons."""
    res = ('{}:' * len(attrs)).format(*[getr(node, a) for a in attrs])[:-1]
    return res


def getr(obj, toget):
    """Getattr with dots."""
    res = obj
    for attr in toget.split('.'):
        res = getattr(res, attr)
        if res is None:
            break
    return res
