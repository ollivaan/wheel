
import dash
import dash_table
import random
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from .layout import html_layout
from pathlib import Path
import json



def sunburst_parents():
    """Returns the parents for sunburst graph"""
    df_economy,df_process,df_society,df_environment = define_dataframes()
    company_name = [""]+["Corporation"]*4
    closest_category = (["Economy"]*3+["Process"]*5+["Society"]*5+["Environment"]*9)[::-1]
    parents = company_name
    result = pd.concat([df_economy, df_process, df_society, df_environment],axis=1)
    column_names = result.columns.get_level_values(0).to_list()[::-1]

    prev_main_column = ""
    for i in range(len(result.columns)):
        main_column, sub_column = result.columns[i]
        if(len(parents)==5):
            parents.append(closest_category.pop())
            parents.append(column_names.pop())
        if(prev_main_column==""):
            prev_main_column=main_column
            parents += result[str(main_column)][str(sub_column)][0:3].values.tolist()
        elif(main_column==prev_main_column):
            parents.append(column_names.pop())
            parents += result[str(main_column)][str(sub_column)][0:3].values.tolist()
        else:
            prev_main_column=main_column
            parents.append(closest_category.pop())
            parents.append(column_names.pop())
            parents += result[str(main_column)][str(sub_column)][0:3].values.tolist()
        
    return parents

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]



def sunburst_labels():
    """Returns the labels for sunburst graph"""
    root_labels = ["", 'Economy', 'Process','Society','Environment']
    df_economy,df_process,df_society,df_environment = define_dataframes()
    result = pd.concat([df_economy, df_process, df_society, df_environment],axis=1)
    column_names = unique(result.columns.get_level_values(0).to_list()[::-1])
    column_names = list(column_names)
    
    prev_main_column = ""
    for i in range(len(result.columns)):
        main_column, sub_column = result.columns[i]
        if(len(root_labels)==5):
            root_labels.append(column_names.pop())
            root_labels += result[str(main_column)][str(sub_column)][0:4].values.tolist()
        elif(prev_main_column==""):
            prev_main_column=main_column
            root_labels += result[str(main_column)][str(sub_column)][0:4].values.tolist()
        elif(main_column==prev_main_column):
            root_labels += result[str(main_column)][str(sub_column)][0:4].values.tolist()
        else:
            prev_main_column=main_column
            root_labels.append(column_names.pop())
            root_labels += result[str(main_column)][str(sub_column)][0:4].values.tolist()
    return root_labels



def join_dataframes():
    """Returns the joined dataframe without upper column index"""
    df_economy,df_process,df_environment,df_society = define_dataframes()
    result = pd.concat([df_economy, df_process, df_society, df_environment],axis=1)
    df_result = result.T.reset_index(level=[1]).T

    return (df_result)

def sundata():
    load_ring_values()
    """Defines colors and sets the necessary attributes for sunburst graph"""
    answers = Path("data/user_answers.csv")
    colors = ["pink",'skyblue','thistle','lightslategray','lightblue']+['lightskyblue']*23+['thistle']*45+['lightslategray']*57+['lightblue']*95

    if answers.is_file():
        with open("data/user_answers.csv") as f:
            lines = f.readlines()

        numbers =[float(e.strip()) for e in lines]
        print("")
        if (((sum(numbers)/len(numbers)) > 0.5)):
            starter_colors = ['','palegreen','lightblue','lightblue','lightblue']
        else:
            starter_colors = ['','crimson','lightblue','lightblue','lightblue'] 

        colors_by_answers = starter_colors+['palegreen' if val >0.1 else 'crimson' for val in numbers]
        colors_d = {"line": {"width":3},"colors":colors_by_answers}
    else:
        """If there's no values in user_ansers.csv then default (answers will be deleted every time)"""
        colors_d = {"line": {"width":3},"colors":colors}

    fig = go.Sunburst(
        labels=sunburst_labels(),
        parents=sunburst_parents(),
        opacity=0.8,
        textfont = {'size': 15},
        insidetextorientation = 'horizontal',
        marker=colors_d,)
    layout = go.Layout(hovermode='closest', height=775, width=1250,margin=go.layout.Margin(t=0, l=0, r=0, b=0))
    return {'data': [fig], 'layout': layout}

def load_ring_values():
    """Loads ring values"""
    f = open('data/ringvalues.json',) 
    data = json.load(f) 
    first_inner_ring = [i for i in data['first_inner_ring']]
    second_inner_ring = [i for i in data['second_inner_ring']]
    outer_ring = [i for i in data['outer_ring']]
    f.close()
    return first_inner_ring,second_inner_ring,outer_ring


def modified_ring_values():
    """Modifies ring values ie. add <br > so the sunburst graph knows which words can be splitted"""
    first_inner_ring,second_inner_ring,outer_ring = load_ring_values()
    outer_ring_modified = []
    for i in range(len(outer_ring)):
        if(' ' in outer_ring[i]):
            outer_ring_modified.append(outer_ring[i].replace(" ", " <br > "))
        else:
            outer_ring_modified.append(outer_ring[i])

    second_inner_ring_modified = []
    for i in range(len(second_inner_ring)):
        if(' ' in second_inner_ring[i]):
            second_inner_ring_modified.append(second_inner_ring[i].replace(" ", " <br > "))
        else:
            second_inner_ring_modified.append(second_inner_ring[i])

    return (first_inner_ring,second_inner_ring_modified,outer_ring_modified)


def define_dataframes():
    """Creates and defines "MultiIndex" dataframes for each sector"""
    second_inner_ring,mid_questions,outer_ring = modified_ring_values()
    second_inner_ring_divided = second_inner_ring[0:3] + second_inner_ring[3:8] + second_inner_ring[8:12] + second_inner_ring[12:22]

    second_inner_sub_categories = []
    for i in range(len(second_inner_ring_divided)):
        if(second_inner_ring_divided[i]=="Reputation"
           or second_inner_ring_divided[i]=="Communication" 
           or second_inner_ring_divided[i]=="Food"):
            second_inner_sub_categories.append(second_inner_ring_divided[i])
        elif(second_inner_ring_divided[i]=="Planning"
             or second_inner_ring_divided[i]=="Community"
             or second_inner_ring_divided[i]=="Materials"
             or second_inner_ring_divided[i]=="Water"):
            second_inner_sub_categories.append(second_inner_ring_divided[i])
            second_inner_sub_categories.append(second_inner_ring_divided[i])
            second_inner_sub_categories.append(second_inner_ring_divided[i])
        elif(second_inner_ring_divided[i]=="Wellbeing"):
            second_inner_sub_categories.append(second_inner_ring_divided[i])
            second_inner_sub_categories.append(second_inner_ring_divided[i])
            second_inner_sub_categories.append(second_inner_ring_divided[i])
            second_inner_sub_categories.append(second_inner_ring_divided[i])
        else:
            second_inner_sub_categories.append(second_inner_ring_divided[i])
            second_inner_sub_categories.append(second_inner_ring_divided[i])
            
    economy_sub = ['one', 'two', 'one', 'two','one']
    economy = [second_inner_sub_categories[0:5],economy_sub]
    
    economy_tuples = list(zip(*economy))
    columns = pd.MultiIndex.from_tuples(economy_tuples)
    df_economy = pd.DataFrame(columns=columns)

#    df_economy_zeros = pd.DataFrame(np.zeros((4, 5)),columns=columns,index=["economy 1","economy 2","economy 3","economy 4"], dtype=int)
    df_economy['Finance', 'one'] = mid_questions[0:3]+outer_ring[0:1]
    df_economy['Finance', 'two'] = mid_questions[3:6]+outer_ring[1:2]
    df_economy['Employment', 'one'] = mid_questions[6:9]+outer_ring[2:3]
    df_economy['Employment', 'two'] = mid_questions[9:12]+outer_ring[3:4]
    df_economy['Reputation', 'one'] = mid_questions[12:15]+outer_ring[4:5]
    
    process_sub = ["one","one","two","one","two","three","one","two","one","two"]
    process = [second_inner_sub_categories[5:15],process_sub]
    
    process_tuples = list(zip(*process))
    columns = pd.MultiIndex.from_tuples(process_tuples)
    df_process = pd.DataFrame(columns=columns)
#    df_process_zeros = pd.DataFrame(np.zeros((4, 10)),columns=columns,index=["process 1","process 2","process 3","process 4"], dtype=int)
    df_process['Communication', 'one'] = mid_questions[15:18]+outer_ring[5:6]
    df_process['Knowledge', 'one'] = mid_questions[18:21]+outer_ring[6:7]
    df_process['Knowledge', 'two'] = mid_questions[21:24]+outer_ring[7:8]
    df_process['Planning', 'one'] = mid_questions[24:27]+outer_ring[8:9]
    df_process['Planning', 'two'] = mid_questions[27:30]+outer_ring[9:10]
    df_process['Planning', 'three'] = mid_questions[30:33]+outer_ring[10:11]
    df_process['Delivery', 'one'] = mid_questions[33:36]+outer_ring[11:12]
    df_process['Delivery', 'two'] = mid_questions[36:39]+outer_ring[12:13]
    df_process['Product', 'one'] = mid_questions[39:42]+outer_ring[13:14]
    df_process['Product', 'two'] = mid_questions[42:45]+outer_ring[14:15]
    
    society_sub = ["one","two","one","two","three","four","one","two","one","two","three","one","two"]
    society = [second_inner_sub_categories[15:28],society_sub]
    
    society_tuples = list(zip(*society))
    columns = pd.MultiIndex.from_tuples(society_tuples)
    df_society = pd.DataFrame(columns=columns)
#    df_society_zeros = pd.DataFrame(np.zeros((4, 13)),columns=columns, index=["society 1","society 2","society 3","society 4"],dtype=int)
    df_society['Mobility', 'one'] = mid_questions[45:48]+outer_ring[15:16]
    df_society['Mobility', 'two'] = mid_questions[48:51]+outer_ring[16:17]
    df_society['Wellbeing', 'one'] = mid_questions[51:54]+outer_ring[17:18]
    df_society['Wellbeing', 'two'] = mid_questions[54:57]+outer_ring[18:19]
    df_society['Wellbeing', 'three'] = mid_questions[57:60]+outer_ring[19:20]
    df_society['Wellbeing', 'four'] = mid_questions[60:63]+outer_ring[20:21] 
    df_society['Engagement', 'one'] = mid_questions[63:66]+outer_ring[21:22]
    df_society['Engagement', 'two'] = mid_questions[66:69]+outer_ring[22:23]
    df_society['Community', 'one'] = mid_questions[69:72]+outer_ring[23:24]
    df_society['Community', 'two'] = mid_questions[72:75]+outer_ring[24:25]
    df_society['Community', 'three'] = mid_questions[75:78]+outer_ring[25:26]
    df_society['Ethics', 'one'] = mid_questions[78:81]+outer_ring[26:27]
    df_society['Ethics', 'two'] = mid_questions[81:84]+outer_ring[27:28]
    
    environment_sub = ["one","one","two","one","two","three","one","two","one","two","three","one","two","one","two","one","two","one","two"]
    environment = [second_inner_sub_categories[28:47],environment_sub]
    environment_tuples = list(zip(*environment))
    columns = pd.MultiIndex.from_tuples(environment_tuples)
    df_environment = pd.DataFrame(columns=columns)
#    df_environment_zeros = pd.DataFrame(np.zeros((4, 19)),columns=columns, index=["environment 1","environment 2","environment 3","environment 4"],dtype=int)
    df_environment['Food','one'] = mid_questions[84:87]+outer_ring[28:29]
    df_environment['Land','one'] = mid_questions[87:90]+outer_ring[29:30]
    df_environment['Land','two'] = mid_questions[90:93]+outer_ring[30:31]
    df_environment['Materials','one'] = mid_questions[93:96]+outer_ring[31:32]
    df_environment['Materials','two'] = mid_questions[96:99]+outer_ring[32:33]
    df_environment['Materials','three'] = mid_questions[99:102]+outer_ring[33:34]
    df_environment['Ecology','one'] = mid_questions[102:105]+outer_ring[34:35]
    df_environment['Ecology','two'] = mid_questions[105:108]+outer_ring[35:36]
    df_environment['Water','one'] = mid_questions[108:111]+outer_ring[36:37]
    df_environment['Water','two'] = mid_questions[111:114]+outer_ring[37:38]
    df_environment['Water','three'] = mid_questions[114:117]+outer_ring[38:39]
    df_environment['Air','one'] = mid_questions[117:120]+outer_ring[39:40]
    df_environment['Air','two'] = mid_questions[120:123]+outer_ring[40:41]
    df_environment['Climate','one'] = mid_questions[123:126]+outer_ring[41:42]
    df_environment['Climate','two'] = mid_questions[126:129]+outer_ring[42:43]
    df_environment['Energy','one'] = mid_questions[129:132]+outer_ring[43:44]
    df_environment['Energy','two'] = mid_questions[132:135]+outer_ring[44:45]
    df_environment['Environmental impact','one'] = mid_questions[135:138]+outer_ring[45:46]
    df_environment['Environmental impact','two'] = mid_questions[138:142]+outer_ring[46:47]
    return (df_economy,df_process,df_society,df_environment)