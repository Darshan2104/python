'''
Google Interview Question : 

=> Problem Statement:
You are given a circular necklace composed of diamonds (`'D'`) and rubies (`'R'`). 
Your task is to determine whether it's possible to cut the necklace into a contiguous segment such that 
the segment contains exactly half the total number of diamonds and half the total number of rubies. 
If such a segment exists, return its indices in the original string (considering circular wrapping); 
otherwise, return "No Solution possible".

'''

necklace = "DRRRDRDDDD"


D_count = 0
R_count = 0

for c in necklace:
    if c == 'D':
        D_count += 1
    elif c == 'R':
        R_count += 1

if D_count%2 == 0 and R_count%2 == 0:
    expected_d_count = D_count // 2
    expected_r_count = R_count // 2
    window_size = expected_d_count + expected_r_count
    
    new_necklace = necklace+necklace
    from collections import Counter
    flag = False
    for i in range(len(new_necklace)):
        sub_necklace = new_necklace[i:i+window_size]
        c = Counter(sub_necklace)
        if c['D'] == expected_d_count:
            print([i, i + window_size-1])
            print(sub_necklace)
            flag = True
            break
    if not flag:
        print("No Solution possible")
    # 2 + 3 = 5
else:
    print("No Solution possible")