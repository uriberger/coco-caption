from pycocotools.coco import COCO
from pycocoevalcap.eval import COCOEvalCap
import sys
import os
import json
import statistics
import shutil

assert len(sys.argv) > 3, 'Please provide at least 2 files: reference and predictions file'
lang = sys.argv[1]
reference_file = sys.argv[2]
xm3600_mode = False
xm3600_tmp_dir = 'xm3600_tmp_dir'
if 'crossmodal' in reference_file or 'cross_modal' in reference_file or 'xm3600' in reference_file:
    print('***NOTE: Using XM3600 mode')
    xm3600_mode = True
    if os.path.isdir(xm3600_tmp_dir):
        shutil.rmtree(xm3600_tmp_dir)
prediction_files = sys.argv[3:]

def adjust_xm3600_image_ids(file_path):
    if not os.path.isdir(xm3600_tmp_dir):
        os.mkdir(xm3600_tmp_dir)
        cur_ind = 0
    else:
        cur_ind = max([int(x.split('.json')[0]) for x in os.listdir(xm3600_tmp_dir)]) + 1
    with open('annotations/xm3600_image_ids.json', 'r') as fp:
        image_ids = json.load(fp)
    with open(file_path, 'r') as fp:
        data = json.load(fp)
    orig_to_new_image_id = {image_ids[i]: i for i in range(len(image_ids))}
    for i in range(len(data)):
        data[i]['image_id'] = orig_to_new_image_id[data[i]['image_id']]
    new_file_path = os.path.join(xm3600_tmp_dir, f'{cur_ind}.json')
    with open(new_file_path, 'w') as fp:
        fp.write(json.dumps(data))
    return new_file_path

for pred_file in prediction_files:
    file_name = pred_file.split('/')[-1]
    dir_path = '/'.join(pred_file.split('/')[:-1])
    file_parts = file_name.split('@')
    assert len(file_parts) == 3
    options = file_parts[1].split(',')
    file_names = [file_parts[0] + x + file_parts[2] for x in options]
    file_paths = [os.path.join(dir_path, x) for x in file_names]

    res = []
    for file_path in file_paths:
        coco = COCO(reference_file)
        if xm3600_mode:
            file_path = adjust_xm3600_image_ids(file_path)
        cocoRes = coco.loadRes(file_path)
        cocoEval = COCOEvalCap(coco, cocoRes)
        res.append(cocoEval.evaluate(lang))
    print('>>>>>>>>>>')
    print(pred_file)
    if len(res) == 1:
        print({x[0]: round(x[1], 3) for x in res[0].items()})
    else:
        means = {x: statistics.mean([y[x] for y in res]) for x in res[0].keys()}
        stdevs = {x: statistics.stdev([y[x] for y in res]) for x in res[0].keys()}
        print({x[0]: f'{round(x[1], 3)} +- {round(stdevs[x[0]], 3)}' for x in means.items()})
    print('<<<<<<<<<<')
if xm3600_mode:
    shutil.rmtree(xm3600_tmp_dir)
print('Finished')
