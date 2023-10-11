
import pandas as pd
import numpy as np
from pulp import *


test = [
2500,
4200,
1220,
1500,
1500,
3450,
1350,
2133,
5625,
3200,
3360,
2027,
3000,
2500,
3750,
2750,
1800,
1820,
6500,
2000,
3000,
3000,
3000,
2700,
2400,
2000,
1500,
2908]

name_list = [
"test_2500",
"test_4200",
"test_1220",
"test_1500",
"test_1500",
"test_3450",
"test_1350",
"test_2133",
"test_5625",
"test_3200",
"test_3360",
"test_2027",
"test_3000",
"test_2500",
"test_3750",
"test_2750",
"test_1800",
"test_1820",
"test_6500",
"test_2000",
"test_3000",
"test_3000",
"test_3000",
"test_2700",
"test_2400",
"test_2000",
"test_1500",
"test_2908"
]
name_list = (pd.DataFrame(name_list, columns=['volume_name'])
             .reset_index()
                .rename(columns={'index':'num_volumn'}))



num = len(test)
# max_pair = int(num/2) - 2
for max_pair in range(int(num/2), 0, -1):
    print(max_pair)
    dat=(pd.DataFrame(test, columns=['volume'])
        .reset_index()
        .rename(columns={'index':'id'}))

    dat_dict = dat.to_dict('index')


    # dummy set 
    dummy_set = {}
    for num_volumn in range(0, num):
        for num_pair in range(0, max_pair):
            dummy_set[num_volumn, num_pair] = 'dummy_{}_{}'.format(num_volumn, num_pair)

    # contraint set
    # constraint 1
    constraint_set = {}
    for num_pair in range(0, max_pair):
        constraint_set[num_pair] = 0

    # constraint 2
    constraint_set1 = {}
    for num_volumn in range(0, num):
        constraint_set1[num_volumn] = 0

    # constraint 3
    constraint_set2 = {}
    for num_pair in range(0, max_pair):
        constraint_set2[num_pair] = 0


    # Create the 'prob' variable to contain the problem data
    prob = LpProblem("find the max volume", LpMinimize)

    #spot dummy variable
    dummy_result = {}
    for num_volumn in range(0, num):
        for num_pair in range(0, max_pair):
            dummy_result[num_volumn, num_pair] = LpVariable(dummy_set[num_volumn, num_pair], cat = 'Binary')

    # optimal function
    opt = 0
    for num_volumn in range(0, num):
        for num_pair in range(0, max_pair):
            opt += dummy_result[num_volumn, num_pair]
    prob += opt

    # constraint 1
    for num_pair in range(0, max_pair):
        for num_volumn in range(0, num):
            constraint_set[num_pair]+=dummy_result[num_volumn, num_pair]*dat_dict[num_volumn]['volume']
        prob += constraint_set[num_pair] >= 8000, "constraint_1_"+str(num_pair)

    # constraint 2
    for num_volumn in range(0, num):
        for num_pair in range(0, max_pair):
            constraint_set1[num_volumn]+=dummy_result[num_volumn, num_pair]
        prob += constraint_set1[num_volumn] <= 1, "constraint_2_"+str(num_volumn)

    # constraint 3
    for num_pair in range(0, max_pair):
        for num_volumn in range(0, num):
            constraint_set2[num_pair]+=dummy_result[num_volumn, num_pair]
        prob += constraint_set2[num_pair] <= 5, "constraint_3_"+str(num_pair)


    # print(prob)
    prob.solve()
    print("Status:", LpStatus[prob.status])
    if LpStatus[prob.status] == 'Optimal':
        break
result = []
for v in prob.variables():
    result.append([v.name, v.varValue])

result = pd.DataFrame(result, columns=['name', 'value'])
result['num_volumn'] = result['name'].apply(lambda x: x.split('_')[1]).astype(int)
result['num_pair'] = result['name'].apply(lambda x: x.split('_')[2]).astype(int)

result = (result
          .merge(dat, left_on='num_volumn', right_on='id', how='left')
)
result['volumexvalue'] = result['volume']*result['value']
result = (result
          .merge(name_list, on='num_volumn', how='left')
)
output_result = (result
          .query('value > 0')
          .sort_values(['num_pair', 'num_volumn'])
)


result = (
    pd.pivot_table(result, 
                   index='num_volumn',
                   columns='num_pair', 
                   values='volumexvalue')
    
)


result.to_csv('result.csv')
output_result.to_csv('output_result.csv')
