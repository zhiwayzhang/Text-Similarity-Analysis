import pandas as pd
import numpy as np
import nltk

description_x = []
description_y = []

data = pd.read_csv('./data.csv')

ids = data['id']
text = data['text']

test_id = [i for i in range(0, len(text))]
cnt = 0
tt = 6973
for i in text:
    description_x.append(text[tt])
    description_y.append(i)

outfile = pd.DataFrame({"test_id": test_id,"description_x": description_x, "description_y": description_y})

outfile.to_csv("singleData.csv", index = False)
