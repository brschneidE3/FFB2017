from multiprocessing import Pool

def f(x):
    return x*x

print 'this is a test'

if __name__ == '__main__':
    values_dict = {}
    L = [1, 2, 3]

    p = Pool(5)
    values = list(p.imap(f, L))

    for i in range(len(L)):
        key = L[i]
        value = values[i]
        values_dict[key] = value

    print values_dict