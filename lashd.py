import argparse
import re


parser = argparse.ArgumentParser()
parser.add_argument('filename')
parser.add_argument('parameter')
parser.add_argument('output')
args = parser.parse_args()


def filehandler():
    # read input file
    with open(args.filename) as f:
        inp = f.readlines()
        f.close()
    transac = []
    for line in inp:
        pattern = re.findall(r'{.*}', line)
        transac.extend(pattern)
    # read parameter file
    with open(args.parameter) as p:
        para = p.readlines()
        p.close()
    MS_val = {}
    cant_be = []
    must_have = []
    for line in para:
        if line.startswith('MIS'):  # MIS values
            MS_pat = re.search(r'.*\((\w*)\) = (\d*\.\d*)', line)
            MS_val[MS_pat.group(1)] = MS_pat.group(2)
        elif line.startswith('SDC'):    #support difference constraint
            SDC_pat = re.findall(r'\d\.\d', line)
            SDC_val = float(SDC_pat[0])
        elif line.startswith('can'):    #cannot be together
            cant_pat = re.findall("{(\d+(,*\s*\d+)*)}", line)
            for x in cant_pat:
                items = re.findall(r"\d+", x[0])
                items = [str(i) for i in items]
                cant_be.append(items)
        elif line.startswith('must'):   #must have
            must_have = re.findall(r'\d+', line)
         
    return transac, MS_val, SDC_val, cant_be, must_have
transac, MS_val, SDC_val, cant_be, must_have = filehandler()



# calculate frequent-2 itemsets
def cand2gen(L, SDC_val):
    C = []
    for index, item in enumerate(L):
        if count_sup[item]/n > float(MS_val[item]):
            for j in range(index+1, len(L)):
                if count_sup[L[j]]/n > float(MS_val[item]) and \
                 abs(count_sup[L[j]]/n - count_sup[item]/n) <= SDC_val:
                    C.append([item, L[j]])
    return C

# calculate frequent-n itemsets
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
                    Ck.append(C)    # join step
                    
    for item in Ck:
            c = Ck.index(item)
            subset = []
            for i in item:
                gensubset = []
                comb = item.index(i)
                gensubset = item[:comb]+item[comb+1:]
                subset.append(gensubset)
            
            for j in subset:
                if item[0] in j or MS_val[item[0]]==MS_val[item[1]]:
                    if j not in F:
                        del Ck[c]   #prune step
                        break   
    return Ck


# apply must have and cannot be together conditions
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


# print results
def print_in_format(F):
    with open(args.output, 'w+') as output:
        for item in F:
            output.write('Frequent ' + str(item) + '-itemsets\n')
            for initem in F[item]:
                if item == 1:
                    output.write('\n    ' + str(count_sup[initem[0]]) + ' : {' + ','.join(set(initem)) + '}')
                else:
                    tail_count = 0
                    for c in cand[item]:
                        if set(c) == set(initem):
                            count = count_sup.get(tuple(c))
                    if item == 2:   # tailcout generation
                        tail_count = count_sup[initem[item-1]]
                    else:
                        for c in cand[item-1]:
                            if set(c) == set(initem[1:]):
                                tail_count = count_sup.get(tuple(c))
                    output.write("\n    " + str(count) + " : " + '{' + ', '.join(initem) + '}')
                    output.write("\nTailcount = " + str(tail_count))
            output.write("\n\n    Total number of frequent "+ str(item) + "-itemsets = " + str(len(F[item])) + "\n\n\n")


count_sup = {}     # dict to calculate support count of each item
translist = []     # list to count item occurances in transactions  
L = []             # first pass over transactions
koko = []          
F1 = []            # frequent-1 itemsets
sorted_MIS = []    # items sorted by minimum support
Freq = {}          # dict of frequent itemsets
cand = {}          # dict of candidate itemsets
n = len(transac)   # number of transactions

transac = [x.replace("{", "").replace("}", "").replace(" ", "") for x in transac]
for item in transac:
    translist.append(item.split(","))

# calsulating support of all items
for item in translist:
    for minitem in item:
        count_sup[minitem] = count_sup.get(minitem, 0) + 1

# smallest MIS value
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
        F1.append([item])  # frequent-1 itemsets generated
Freq[1] = F1


k = 2
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


Fb = with_conditions(Freq, must_have, cant_be)
print_in_format(Fb)
