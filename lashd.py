import argparse
import re
import itertools

parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('parameter')
parser.add_argument('output')
args = parser.parse_args()

def cand2gen(L, SDC_val):
    C = []
    for index, item in enumerate(L):
        if count_sup[item]/n > float(MS_val[item]):
            for j in range(index+1, len(L)):
                if count_sup[L[j]]/n > float(MS_val[item]) and \
                 abs(count_sup[L[j]]/n - count_sup[item]/n) <= SDC_val:
                    C.append([item, L[j]])
    return C

def subsets(itemset):
    subset = []
    for i in itemset:
        j = []
        p = itemset.index(i)
        j = itemset[:p]+itemset[p+1:]
        subset.append(j)
    return subset
def candngen(F, SDC_val):
    Ck = []
    for i, item in enumerate(F):
        for j, initem in enumerate(F):
            if item[:-1] == initem[:-1] and item[-1] < initem[-1]:
                if abs(count_sup[item[-1]]/n - count_sup[initem[-1]]/n) <=\
                 SDC_val:
                    C = []
                    C.extend(item)
                    C.append(initem[-1])
                    # print(C)
                    Ck.append(C)
                    
    for item in Ck:
            c = Ck.index(item)
            subset = []
            subset = subsets(item)
            for j in subset:
                if item[0] in j or MS_val[item[0]]==MS_val[item[1]]:
                    if j not in F:
                        del Ck[c]
                        break   
    return Ck

def with_conditions(F, must_have, cant_be):
    F1 = {}
    for k in F:
        F1[k] = []
        for f in F[k]:
            delete = False
            if set(f).intersection(set(must_have)):
                for c in cant_be:
                    if set(c).issubset(set(f)):
                        delete = True
                        break
                if not delete:
                    F1[k].append(f)
    return F1

def print_in_format(F):
    with open(args.output, 'w+') as o:
        for item in F:
            o.write('Frequent ' + str(item) + '-itemsets\n')
            for initem in F[item]:
                if item == 1:
                    o.write('\n    ' + str(count_sup[initem[0]]) + ' : {' + ','.join(set(initem)) + '}')
                else:
                    tail_count = 0
                    for c in cand[item]:
                        if set(c) == set(initem):
                            count = count_sup.get(tuple(c))
                    if item == 2:
                        tail_count = count_sup[initem[item-1]]
                    else:
                        for c in cand[item-1]:
                            if set(c) == set(initem[1:]):
                                tail_count = count_sup.get(tuple(c))
                    o.write("\n    " + str(count) + " : " + '{' + ', '.join(initem) + '}')
                    o.write("\nTailcount = " + str(tail_count))
            o.write("\n\n    Total number of frequent "+ str(item) + "-itemsets = " + str(len(F[item])) + "\n\n\n")

def filehandler():

    with open(args.filename) as f:
        inp = f.readlines()
        f.close()
    transac = []
    for line in inp:
        pattern = re.findall(r'{.*}', line)
        transac.extend(pattern)
    with open(args.parameter) as p:
        para = p.readlines()
        p.close()
    MS_val = {}
    cant_be = []
    must_have = []
    for line in para:
        if line.startswith('MIS'):
            MS_pat = re.search(r'.*\((\w*)\) = (\d*\.\d*)', line)
            MS_val[MS_pat.group(1)] = MS_pat.group(2)
        elif line.startswith('SDC'):
            SDC_pat = re.findall(r'\d\.\d', line)
            SDC_val = float(SDC_pat[0])
        elif line.startswith('can'):
            group = re.findall("{(\d+(,*\s*\d+)*)}", line)
            for g in group:
                items = re.findall(r"\d+", g[0])
                items = [str(i) for i in items]
                cant_be.append(items)
        elif line.startswith('must'):
            must_have = re.findall(r'\d+', line)
         
    return transac, MS_val, SDC_val, cant_be, must_have

count_sup = {}     # dict to calculate support count of each item
translist = []
L = []
koko = []
F1 = []
sorted_MIS = []
C2 = []
Freq = {}
cand = {}
k = 2
transac, MS_val, SDC_val, cant_be, must_have = filehandler()
transac = [x.replace("{", "").replace("}", "").replace(" ", "") for x in transac]
n = len(transac)

for item in transac:
    translist.append(item.split(","))

for item in translist:
    for minitem in item:
        count_sup[minitem] = count_sup.get(minitem, 0) + 1

for item, mins in sorted(MS_val.items(), key=lambda x: (x[1], int(x[0]))):
    sorted_MIS.append(item)

minimis = MS_val[sorted_MIS[0]]

for item in sorted_MIS:
    if item in [j for i in translist for j in i]:
        koko.append(item)

for item in koko:
    if count_sup[item]/n > float(minimis):
        L.append(item)    # L calculated

for item in L:
    if count_sup[item]/n > float(MS_val[item]):
        F1.append([item])  # Frequent set 1 generated
Freq[1] = F1
while k >= 2:
    if not Freq[k - 1]:
        break
    if k is 2:
        cand[k] = cand2gen(L, SDC_val)
    else:
        cand[k] = candngen(Freq[k-1], SDC_val)
    F = []
    for item in translist:
        for i in cand[k]:
            if set(i).issubset(set(item)):
                if count_sup.get(tuple(i)) is None:
                    count_sup[tuple(i)] = 1
                else:
                    count_sup[tuple(i)] = count_sup.get(tuple(i)) + 1
    for i in cand[k]:
        if(count_sup.get(tuple(i)) is not None):
            if count_sup.get(tuple(i))/n >= float(MS_val[i[0]]):
                F.append(i)
    Freq[k] = F
    k += 1

# print(Freq)
Fb = with_conditions(Freq, must_have, cant_be)
print_in_format(Fb)
