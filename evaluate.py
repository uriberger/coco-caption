from pycocotools.coco import COCO
from pycocoevalcap.eval import COCOEvalCap
import sys
import os
import statistics

assert len(sys.argv) > 2, 'Please provide at least 2 files: reference and predictions file'
reference_file = sys.argv[1]
prediction_files = sys.argv[2:]

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
        cocoRes = coco.loadRes(file_path)
        cocoEval = COCOEvalCap(coco, cocoRes)
        res.append(cocoEval.evaluate())
    print('>>>>>>>>>>')
    print(pred_file)
    if len(res) == 1:
        print({x[0]: round(x[1], 3) for x in means.items()})
    else:
        means = {x: statistics.mean([y[x] for y in res]) for x in res[0].keys()}
        stdevs = {x: statistics.stdev([y[x] for y in res]) for x in res[0].keys()}
        print({x[0]: f'{round(x[1], 3)} +- {round(stdevs[x[0]], 3)}' for x in means.items()})
    print('<<<<<<<<<<')
print('Finished')
