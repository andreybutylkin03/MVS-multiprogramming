import xml.etree.ElementTree as ET
import sys
import random
import os.path

def read(file_name, err):  # функция для считывания данных
    file = ET.parse(file_name)  # парсим файл
    root = file.getroot()

    if len(root) != 3:  # проверяем на корректность составления файла
        err.write("wrong file\n")
        exit(0)

    proc = dict()
    prog = dict()
    pair_prog = dict()

    proc_m = set(['50', '70', '90', '100'])  # задание множества допустимых значений
    prog_m = set(['5', '10', '15', '20'])
    pair_prog_m = set(['0', '10', '50', '70', '100'])

    if (root[0].attrib['n'] != str(len(root[0]))):  # проверка на соответствие указанных размеров
        err.write("size mismatch -- processors\n")
        exit(0)
    if (root[1].attrib['m'] != str(len(root[1]))):
        err.write("size mismatch -- program\n")
        exit(0)
    if (root[2].attrib['k'] != str(len(root[2]))):
        err.write("size mismatch -- pair_net\n")
        exit(0)

    for elem in root[0]:  # заполняем proc, prog
        try:
            vr = elem.attrib['value']
        except:
            print("'value' nof found in processors, read instruction", file=err)
            exit(0)

        if elem.attrib['value'] not in proc_m:  # проверяем, что значение допустимо
            err.write(f"invalid value -- {elem.attrib['value']} in processors\n")
            exit(0)

        try:
            proc[int(elem.attrib['proc'])] = int(elem.attrib['value'])
        except:
            print("'proc' nof found in processors, read instruction", file=err)
            exit(0)

    for elem in root[1]:
        try:
            vr = elem.attrib['value']
        except:
            print("'value' nof found in program, read instruction", file=err)
            exit(0)

        if elem.attrib['value'] not in prog_m:
            err.write(f"invalid value -- {elem.attrib['value']} in program\n")
            exit(0)

        try:
            prog[int(elem.attrib['prog'])] = int(elem.attrib['value'])
        except:
            print("'prog' nof found in program, read instruction", file=err)
            exit(0)

    m = len(prog)
    for i in range(m):  # заполняем pair_prog -1
        for j in range(i + 1, m):
            pair_prog[(i, j)] = -1

    for elem in root[2]:  # заполняем pair_prog
        try:
            vr = elem.attrib['intensity']
        except:
            print("'intensity' nof found in pair_net, read instruction", file=err)
            exit(0)

        if elem.attrib['intensity'] not in pair_prog_m:
            err.write(f"invalid value -- {elem.attrib['intensity']} in pair_net\n")
            exit(0)

        try:
            vr = elem.attrib['prog1']
        except:
            print("'prog1' nof found in pair_net, read instruction", file=err)
            exit(0)

        try:
            vr = elem.attrib['prog2']
        except:
            print("'prog2' nof found in pair_net, read instruction", file=err)
            exit(0)

        prog_r = [str(i) for i in range(1, m + 1)]

        if elem.attrib['prog1'] not in prog_r:
            err.write(f"invalid value -- {elem.attrib['prog1']} in pair_net\n")
            exit(0)

        if elem.attrib['prog2'] not in prog_r:
            err.write(f"invalid value -- {elem.attrib['prog2']} in pair_net\n")
            exit(0)

        mi = min((int(elem.attrib['prog1']), int(elem.attrib['prog2'])))
        ma = max((int(elem.attrib['prog1']), int(elem.attrib['prog2'])))
        if mi == ma:
            err.write(f"invalid value -- 'prog1' == 'prog2'\n")
            exit(0)

        if pair_prog[(mi - 1, ma - 1)] != -1:
            print(f"value has been updated before in pair_net", file = err)
            exit(0)

        pair_prog[(mi - 1, ma - 1)] = int(elem.attrib['intensity'])

    for i in range(m):  # обнуляем оставшийся pair_prog
        for j in range(i + 1, m):
            if pair_prog[(i, j)] == -1:
                pair_prog[(i, j)] = 0

    return proc, prog, pair_prog

def f_x(x, pair_prog, f_best): #реализаций функции f(x) с оптимизацией
    m = len(x)
    f = 0

    for i in range(m):
        for j in range(i, m):
            if x[i] != x[j]:
                f += pair_prog[(i, j)]
            if f >= f_best:
                break
        if f >= f_best:
            break

    return f

def exam(x, proc, prog): #функция проверяющая корректность x
    ans = True
    n = len(x)
    m = len(proc)
    proc_c = [0 for i in range(m)]

    for i in range(n):
        proc_c[x[i] - 1] += prog[i + 1]
        if proc_c[x[i] - 1] > proc[x[i]]:
            ans = False
            break

    return ans

def solve(proc, prog, pair_prog):
    n = len(proc)
    m = len(prog)

    vr = [pair_prog[i] for i in pair_prog]
    f_best = sum(vr)
    x_best = [-1 for i in range(m)]
    i = 0
    it = 0
    set_rand = set()

    while i < 5000:
        it += 1
        x = [random.randint(1, n) for i in range(m)]

        if tuple(x) in set_rand: # проверяем на уникальность полученный массив
            i += 1
            continue

        set_rand.add(tuple(x))

        if exam(x, proc, prog) == False:
            i += 1
            continue

        f = f_x(x, pair_prog, f_best)
        if f >= f_best:
            i += 1
            continue

        f_best = f
        x_best = x
        i = 0
        if f == 0:
            break
        
    return x_best, f_best, it

print("Enter the name of the input file:")
file_name = input() #считываем название файла
stderr_out = sys.stderr

if file_name[-4:] != ".xml": #проверяем, что это xml файл 
    stderr_out.write("file is not xml format\n")
    exit(0)

if os.path.exists(file_name) == False: #проверяем существование файла 
    stderr_out.write("file not exist\n")
    exit(0)

proc, prog, pair_prog = read(file_name, stderr_out) 
x_best, f_best, it  = solve(proc, prog, pair_prog)

if -1 in x_best:
    print("failure")
    print("number of algorithm iterations", it)
else:
    print("succes")
    print("number of algorithm iterations", it)
    print("x_best:")
    print(*x_best)
    print("network load:", f_best)